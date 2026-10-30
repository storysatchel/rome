"""Hybrid (semantic + keyword) retrieval over the Antfly `rome` corpus.

Returns the same dict shape as `raw_source_search.search` -- source, locator,
text, snippet, score -- plus `work_id` so callers can count independent works
instead of file encodings. Requires the `antfly-sdk` package and a running
Antfly server (ANTFLY_URL, default http://127.0.0.1:18080).

Locators: PDF hits carry the PDF *file* page (`p.N`), which is not the printed
page; EPUB and text hits carry the chunk ordinal (`chunk.N`).
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Iterable

FIELDS = ["source_relative_path", "page_numbers", "section", "body", "chunk_index", "previous_id", "next_id"]
OVERRIDES_PATH = Path(__file__).with_name("work_ids.json")
_KNOWN_SUFFIXES = {".pdf", ".epub", ".txt", ".azw3", ".djvu", ".decrypted"}
_FORMAT_SUFFIX = re.compile(r"(?:epub|pdf)$")
_COPY_MARK = re.compile(r"\s*\(\d+\)$")
SHINGLE_WORDS = 6
DUPLICATE_OVERLAP = 0.5


def load_overrides(path: Path = OVERRIDES_PATH) -> dict[str, str]:
    """Curated {normalized-stem: work_id}; collapses translations/editions by hand."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_stem(source_relative_path: str) -> str:
    """Filename stem with format, decrypted and copy markers and case removed.

    Corpus filenames glue the format onto the title ("Liviaepub.pdf",
    "Liviaepub.decrypted.epub"), so every file encoding of one book maps to one stem.
    """
    stem = Path(source_relative_path).name
    while Path(stem).suffix.lower() in _KNOWN_SUFFIXES:
        stem = Path(stem).stem
    stem = _COPY_MARK.sub("", stem)
    stem = _FORMAT_SUFFIX.sub("", unicodedata.normalize("NFKD", stem).casefold().strip())
    return re.sub(r"[^\w]+", "-", stem).strip("-")


def work_id(source_relative_path: str, overrides: dict[str, str] | None = None) -> str:
    stem = normalized_stem(source_relative_path)
    return (overrides or {}).get(stem, stem)


def logical_source(source_relative_path: str) -> str:
    """Vault-rooted path: `_archived/X` -> `_raw/X`, `_extracted/X` -> `_raw/_extracted/X`."""
    head, _, rest = source_relative_path.partition("/")
    return f"_raw/{rest}" if head == "_archived" else f"_raw/{source_relative_path}" if head == "_extracted" else source_relative_path


def locator(properties: dict) -> str:
    pages = properties.get("page_numbers") or []
    if pages:
        return f"p.{pages[0]}" if len(pages) == 1 else f"p.{pages[0]}-{pages[-1]}"
    return f"chunk.{properties.get('chunk_index')}"


def _shingles(text: str) -> set[int]:
    """Hashes of word n-grams; ignores spacing and punctuation damage, so the same
    passage extracted from a PDF and from a text file overlaps even when the chunk
    boundaries differ."""
    words = re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold())
    if len(words) < SHINGLE_WORDS:
        return {hash(tuple(words))} if words else set()
    return {hash(tuple(words[i:i + SHINGLE_WORDS])) for i in range(len(words) - SHINGLE_WORDS + 1)}


def _scores(hit) -> dict:
    scores = getattr(hit, "field_index_scores", None)
    extra = getattr(scores, "additional_properties", None)
    return dict(extra) if isinstance(extra, dict) else {}


def hits_to_results(hits: Iterable, overrides: dict[str, str] | None = None,
                    sources: Iterable[str] | None = None, limit: int = 10,
                    dedupe_variants: bool = True, works: Iterable[str] | None = None,
                    exclude_works: Iterable[str] | None = None) -> list[dict]:
    wanted, only, skip = set(sources or []), set(works or []), set(exclude_works or [])
    results, kept = [], {}
    for hit in hits:
        props = dict(hit.field_source.additional_properties)
        relative = props.get("source_relative_path", "")
        source = logical_source(relative)
        wid = work_id(relative, overrides)
        if (wanted and source not in wanted) or (only and wid not in only) or wid in skip:
            continue
        text = props.get("body", "")
        shingles = _shingles(text)
        if dedupe_variants and shingles and any(
                len(shingles & other) / len(shingles) >= DUPLICATE_OVERLAP for other in kept.get(wid, [])):
            continue  # same passage already returned from another file encoding of this work
        kept.setdefault(wid, []).append(shingles)
        results.append({"source": source, "locator": locator(props), "text": text,
                        "snippet": text[:300], "score": hit.field_score, "index_scores": _scores(hit),
                        "work_id": wid, "id": hit.field_id, "previous_id": props.get("previous_id"),
                        "next_id": props.get("next_id"), "section": props.get("section") or []})
        if len(results) >= limit:
            break
    return results


# PDF extraction leaves typographic ligatures in the indexed text, so "pontifical" and
# "pontiﬁcal" are different keyword tokens. Longest forms first so "ffi" wins over "fi".
LIGATURES = (("ffi", "\ufb03"), ("ffl", "\ufb04"), ("ff", "\ufb00"), ("fi", "\ufb01"), ("fl", "\ufb02"))


def keyword_query(query: str) -> str:
    """The query plus a ligature spelling of every word that contains ligature letters."""
    words = query.split()
    variants = []
    for word in words:
        spelled = word
        for plain, ligature in LIGATURES:
            spelled = spelled.replace(plain, ligature)
        if spelled != word:
            variants.append(spelled)
    return " ".join(words + variants)


def _client(client=None):
    if client is not None:
        return client
    from antfly import AntflyClient  # lazy: unit tests and SQLite users need no SDK
    return AntflyClient(os.environ.get("ANTFLY_URL", "http://127.0.0.1:18080"))


def search_antfly(query: str, limit: int = 10, sources: Iterable[str] | None = None,
                  client=None, table: str | None = None, index: str | None = None,
                  dedupe_variants: bool = True, works: Iterable[str] | None = None,
                  exclude_works: Iterable[str] | None = None, keyword_only: bool = False) -> list[dict]:
    """Hybrid search; `keyword_only` skips the semantic half (best for names and exact terms)."""
    if not query.strip():
        raise ValueError("query must not be empty")
    client = _client(client)
    table = table or os.environ.get("ANTFLY_TABLE", "rome")
    index = index or os.environ.get("ANTFLY_INDEX", "body_dense")
    filtered = bool(sources or works or exclude_works)
    fetch = min(limit * 10, 200) if filtered else limit * (3 if dedupe_variants else 1)
    arguments = {"full_text_search": {"match": keyword_query(query)}, "fields": FIELDS, "limit": fetch}
    if not keyword_only:
        arguments.update(semantic_search=query, indexes=[index])
    response = client.query(table, **arguments)
    hits = response.responses[0].hits.hits
    return hits_to_results(hits, load_overrides(), sources, limit, dedupe_variants, works, exclude_works)


def lookup_chunks(chunk_id: str, before: int = 1, after: int = 1, client=None,
                  table: str | None = None) -> list[dict]:
    """The chunk plus up to `before`/`after` neighbours in reading order, same shape as search."""
    client = _client(client)
    table = table or os.environ.get("ANTFLY_TABLE", "rome")
    overrides = load_overrides()

    def fetch(key):
        return client.get(table, key, fields=FIELDS)

    def shape(key, props):
        text = props.get("body", "")
        relative = props.get("source_relative_path", "")
        return {"source": logical_source(relative), "locator": locator(props), "text": text,
                "snippet": text[:300], "work_id": work_id(relative, overrides), "id": key,
                "previous_id": props.get("previous_id"), "next_id": props.get("next_id"),
                "section": props.get("section") or []}

    centre = fetch(chunk_id)
    chain = [shape(chunk_id, centre)]
    props, step = centre, 0
    while props.get("previous_id") and step < before:
        key = props["previous_id"]
        props = fetch(key)
        chain.insert(0, shape(key, props))
        step += 1
    props, step = centre, 0
    while props.get("next_id") and step < after:
        key = props["next_id"]
        props = fetch(key)
        chain.append(shape(key, props))
        step += 1
    return chain
