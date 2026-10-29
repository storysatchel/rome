"""End-to-end staged vault ingestion workflow.

This module owns the safe boundaries around extraction artifacts, deterministic
resolution, Markdown staging, auditing, promotion, and raw-source archiving.
Extraction itself is intentionally an input contract: workers emit one JSON
bundle per source and this coordinator never guesses claims from filenames.
"""
from __future__ import annotations

from collections import defaultdict
import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import unicodedata
import shutil
import sys
import tempfile
from typing import Any, Iterable, Mapping

try:
    from .entity_resolution_engine import CanonicalEntityResolver, ExistingEntity, Mention, normalize
except ImportError:
    from entity_resolution_engine import CanonicalEntityResolver, ExistingEntity, Mention, normalize


CATEGORIES = {"concepts", "entities", "references", "scenarios", "skills", "synthesis", "journal", "projects"}
ARTICLE_TYPES = {"entity": "entities", "concept": "concepts", "scenario": "scenarios", "reference": "references"}
PATCH_SUFFIX = ".patch.md"
REQUIRED_PAGE_FIELDS = ("title", "category", "tags", "sources", "summary", "provenance", "facets")
ALLOWED_RELATIONSHIPS = {"extends", "implements", "contradicts", "derived_from", "uses", "replaces", "related_to", "part_of"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, data: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = data.encode("utf-8") if isinstance(data, str) else data
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def safe_relative(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not value or "\\" in value:
        raise ValueError(f"unsafe relative path: {value!r}")
    return path


def source_key(source_rel: str) -> str:
    return f"src-{hashlib.sha256(source_rel.encode('utf-8')).hexdigest()[:16]}"


def block_name(ordinal: int, block_size: int = 10) -> str:
    if ordinal < 0 or block_size < 1:
        raise ValueError("ordinal must be non-negative and block_size must be positive")
    return f"B{ordinal // block_size:02d}"


@dataclass(frozen=True)
class InventoryRecord:
    source_rel: str
    source_key: str
    content_hash: str
    size_bytes: int
    extension: str
    ordinal: int
    block: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def inventory_sources(vault: Path, raw_dir: str = "_raw", block_size: int = 10) -> list[InventoryRecord]:
    root = (vault / raw_dir).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"raw directory does not exist: {root}")
    files = sorted((item for item in root.iterdir() if item.is_file() and item.name != ".gitkeep"), key=lambda item: item.name)
    records: list[InventoryRecord] = []
    for ordinal, path in enumerate(files):
        relative = path.relative_to(vault).as_posix()
        records.append(InventoryRecord(
            source_rel=relative,
            source_key=source_key(relative),
            content_hash=f"sha256:{sha256_file(path)}",
            size_bytes=path.stat().st_size,
            extension=path.suffix.lower(),
            ordinal=ordinal,
            block=block_name(ordinal, block_size),
        ))
    return records


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    atomic_write(path, "".join(json.dumps(dict(row), sort_keys=True) + "\n" for row in rows))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{number}: expected JSON object")
        rows.append(value)
    return rows


def read_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    marker = text.find("\n---", 4)
    if marker < 0:
        raise ValueError("unterminated YAML frontmatter")
    raw = text[4:marker]
    values: dict[str, Any] = {}
    current_list: str | None = None
    current_mapping: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if current_mapping and line.startswith("  ") and not line.startswith("    "):
            child = re.match(r"^\s{2}([A-Za-z_][A-Za-z0-9_-]*):(?:\s*(.*))?$", line)
            if child:
                values[current_mapping][child.group(1)] = _parse_yaml_scalar(child.group(2) or "")
                continue
        if re.match(r"^\s+-\s+", line) and current_list:
            values.setdefault(current_list, []).append(_strip_yaml_scalar(re.sub(r"^\s+-\s+", "", line)))
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s*(.*))?$", line)
        if not match:
            continue
        key, value = match.group(1), match.group(2) or ""
        if value == "":
            if key in {"aliases", "tags", "sources", "updated_fields", "additions", "deletions", "relationships"}:
                values[key] = []
                current_list = key
                current_mapping = None
            else:
                values[key] = {}
                current_mapping = key
                current_list = None
        else:
            values[key] = _parse_yaml_scalar(value)
            current_mapping = None
            current_list = None
    return values, text[marker + 4 :].lstrip("\n")


def _strip_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _parse_yaml_scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
        return [_strip_yaml_scalar(item) for item in value[1:-1].split(",") if item.strip()]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return _strip_yaml_scalar(value)


def load_existing_entities(vault: Path) -> list[ExistingEntity]:
    entities: list[ExistingEntity] = []
    for category in sorted(CATEGORIES):
        root = vault / category
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            frontmatter, _ = read_frontmatter(text)
            title = str(frontmatter.get("title") or path.stem).strip()
            aliases = tuple(str(item) for item in frontmatter.get("aliases", []) if str(item).strip())
            entities.append(ExistingEntity(path.relative_to(vault).as_posix(), title, aliases))
    return entities


def load_candidate_bundles(candidates_dir: Path, inventory: Mapping[str, InventoryRecord]) -> list[Mention]:
    mentions: list[Mention] = []
    seen_sources: set[str] = set()
    files = sorted(path for path in candidates_dir.iterdir() if path.is_file() and path.suffix == ".json")
    for path in files:
        bundle = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(bundle, dict):
            raise ValueError(f"{path}: candidate bundle must be an object")
        source_rel = str(bundle.get("source_rel", ""))
        if source_rel not in inventory:
            raise ValueError(f"{path}: source_rel is absent from inventory: {source_rel!r}")
        if source_rel in seen_sources:
            raise ValueError(f"duplicate candidate bundle for {source_rel}")
        seen_sources.add(source_rel)
        for raw in bundle.get("mentions", []):
            mentions.append(Mention.from_mapping(raw, source_id=source_rel))
    return mentions


def slugify_title(title: str) -> str:
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower()
    ascii_title = ascii_title.replace("'", "")
    tokens = [token for token in re.split(r"[^a-z0-9]+", ascii_title) if token and token != "and"]
    slug = "-".join(tokens).strip("-")
    if not slug:
        raise ValueError(f"cannot derive slug from title {title!r}")
    return slug


def compile_article_intents(vault: Path, articles_path: Path) -> list[dict[str, Any]]:
    """Compile typed article candidates into deterministic create/patch intents."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in read_jsonl(articles_path):
        article_type = str(record.get("article_type", "")).strip().lower()
        if article_type not in ARTICLE_TYPES or article_type == "reference":
            raise ValueError("article_type must be entity, concept, or scenario")
        title = str(record.get("title", "")).strip()
        if not title:
            raise ValueError("article title is required")
        focus = str(record.get("focus", "")).strip()
        if not focus:
            raise ValueError(f"{title}: focus is required for cohesive article projection")
        category = ARTICLE_TYPES[article_type]
        target_value = str(record.get("target", f"{category}/{slugify_title(title)}.md"))
        target = safe_relative(target_value)
        if re.search(r"(?:^|-)and(?:-|$)", target.stem):
            raise ValueError(f"{target}: filenames must not contain the conjunction 'and'")
        if not target.parts or target.parts[0] != category:
            raise ValueError(f"{article_type} article target must be under {category}/")
        source_values = record.get("sources", record.get("source_rel", []))
        if isinstance(source_values, str):
            source_values = [source_values]
        sources = tuple(sorted({str(item) for item in source_values if str(item).strip()}))
        citations = tuple(sorted({str(item) for item in record.get("citations", []) if str(item).strip()}))
        if not sources or not citations:
            raise ValueError(f"{target}: sources and citations are required")
        grouped[target.as_posix()].append({
            **record,
            "article_type": article_type,
            "category": category,
            "target": target.as_posix(),
            "sources": sources,
            "citations": citations,
            "title": title,
            "focus": focus,
        })

    intents: list[dict[str, Any]] = []
    for target_text in sorted(grouped):
        records = sorted(grouped[target_text], key=lambda item: (item["title"], item["sources"], item["citations"]))
        first = records[0]
        article_type = first["article_type"]
        focuses = {str(record["focus"]) for record in records}
        if len(focuses) != 1:
            raise ValueError(f"{target_text}: same target has conflicting article focuses")
        focus = next(iter(focuses))
        sources = tuple(sorted({source for record in records for source in record["sources"]}))
        citations = tuple(sorted({citation for record in records for citation in record["citations"]}))
        tags = set(str(tag) for record in records for tag in record.get("tags", []))
        tags.add(f"type/{article_type}")
        tags = {tag if "/" in tag else f"subject/{slugify_title(tag)}" for tag in tags}
        if len(tags) > 5:
            raise ValueError(f"{target_text}: article projection exceeds five tags")
        facets: dict[str, list[str]] = {key: [] for key in ("domain", "type", "period", "place", "material", "subject")}
        facets["type"] = [article_type]
        for record in records:
            for facet, values in dict(record.get("facets", {})).items():
                if facet not in facets:
                    raise ValueError(f"{target_text}: unsupported facet {facet!r}")
                if isinstance(values, str):
                    values = [values]
                facets[facet] = sorted(set(facets[facet]).union(str(value) for value in values))
        if article_type not in facets["type"]:
            facets["type"].insert(0, article_type)

        links = sorted({
            str(link).strip()
            for record in records
            for link in record.get("links", record.get("related_pages", []))
            if str(link).strip()
        })
        if len(links) < 2 and not (vault / target_text).exists():
            raise ValueError(f"{target_text}: at least two existing wikilinks are required")
        claims = [claim for record in records for claim in record.get("claims", [])]
        bodies = [str(record["body"]).strip() for record in records if str(record.get("body", "")).strip()]
        sections: list[tuple[str, tuple[str, ...]]] = []
        seen_sections: set[tuple[str, tuple[str, ...]]] = set()
        for record in records:
            raw_sections = record.get("sections", [])
            if isinstance(raw_sections, dict):
                raw_sections = [{"heading": heading, "paragraphs": paragraphs} for heading, paragraphs in raw_sections.items()]
            for section in raw_sections:
                if not isinstance(section, dict):
                    raise ValueError(f"{target_text}: sections must contain objects")
                heading = re.sub(r"[^A-Za-z0-9 /-]+", "", str(section.get("heading", "")).strip()).strip()
                paragraphs = section.get("paragraphs", section.get("content", []))
                if isinstance(paragraphs, str):
                    paragraphs = [paragraphs]
                paragraph_values = tuple(str(paragraph).strip() for paragraph in paragraphs if str(paragraph).strip())
                if not heading or not paragraph_values:
                    raise ValueError(f"{target_text}: each section needs a heading and content")
                section_key = (heading, paragraph_values)
                if section_key not in seen_sections:
                    sections.append(section_key)
                    seen_sections.add(section_key)
        summary = str(first.get("summary", "")).strip()
        if not summary or len(summary) > 200:
            raise ValueError(f"{target_text}: summary is required and must be at most 200 characters")
        body_lines = [f"# {first['title']}", "", f"> [!tldr] {summary}", "", "## Scope", "", focus]
        if sections:
            for heading, paragraphs in sections:
                body_lines.extend(["", f"## {heading}", ""])
                body_lines.extend(paragraphs)
        else:
            body_lines.extend(["", "## Evidence", ""])
            for claim in claims:
                if isinstance(claim, dict):
                    text = str(claim.get("text", "")).strip()
                    citation = str(claim.get("citation", "")).strip()
                else:
                    text, citation = str(claim).strip(), citations[0]
                if text:
                    body_lines.append(f"- {text} {citation}".rstrip())
            for body in bodies:
                body_lines.extend(["", body])
        open_questions = sorted({
            str(question).strip()
            for record in records
            for question in record.get("open_questions", [])
            if str(question).strip()
        })
        if open_questions:
            body_lines.extend(["", "## Open Questions", ""])
            body_lines.extend(f"- {question}" for question in open_questions)
        body_lines.extend(["", "## Related Pages", ""])
        body_lines.extend(f"- [[{link}]]" for link in links)
        body_lines.extend(["", "## Sources", ""])
        body_lines.extend(f"- {source}" for source in sources)
        body_lines.extend(["", "## Citations", ""])
        body_lines.extend(f"- {citation}" for citation in citations)
        body = "\n".join(body_lines).rstrip() + "\n"

        live_target = vault / target_text
        if live_target.exists():
            patch_frontmatter = {
                "target": target_text,
                "operation": "patch",
                "sources": list(sources),
                "updated_fields": ["updated"],
                "updated": utc_now(),
            }
            additions = [f"Scope: {focus}", summary]
            for heading, paragraphs in sections:
                additions.append(f"{heading}: {' '.join(paragraphs)}")
            if not sections:
                additions.extend(
                    str(claim.get("text", claim)).strip() if isinstance(claim, dict) else str(claim).strip()
                    for claim in claims
                )
            additions.extend(open_questions)
            intents.append({
                "target": target_text,
                "operation": "patch",
                "content": render_patch_intent({
                    "frontmatter": patch_frontmatter,
                    "additions": [item for item in additions if item],
                    "citations": list(citations),
                }, target_text),
                "citations": list(citations),
            })
            continue
        frontmatter = {
            "title": first["title"],
            "category": first["category"],
            "scope": focus,
            "tags": sorted(tags),
            "sources": list(sources),
            "summary": summary,
            "provenance": first.get("provenance", {"extracted": 0.7, "inferred": 0.2, "ambiguous": 0.1}),
            "base_confidence": first.get("base_confidence", 0.57),
            "lifecycle": "draft",
            "lifecycle_changed": utc_now()[:10],
            "tier": first.get("tier", "supporting"),
            "created": utc_now(),
            "updated": utc_now(),
            "facets": facets,
        }
        if first.get("aliases"):
            frontmatter["aliases"] = sorted({str(alias) for record in records for alias in record.get("aliases", [])})
        if first.get("relationships"):
            frontmatter["relationships"] = first["relationships"]
        intents.append({
            "target": target_text,
            "operation": "create",
            "frontmatter": frontmatter,
            "citations": list(citations),
            "body": body,
        })
    return intents


def command_compile_articles(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    intents = compile_article_intents(vault, Path(args.articles).resolve())
    output = vault / args.output
    write_jsonl(output, intents)
    print(json.dumps({"intents": len(intents), "output": output.relative_to(vault).as_posix()}))
    return 0
def command_project_candidates(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    try:
        from .candidate_article_projection import build_article_candidates
    except ImportError:
        from candidate_article_projection import build_article_candidates
    candidates = build_article_candidates(vault, vault / args.candidates, args.inventory)
    candidate_output = vault / args.candidate_output
    write_jsonl(candidate_output, candidates)
    intents = compile_article_intents(vault, candidate_output)
    output = vault / args.output
    write_jsonl(output, intents)
    counts = {article_type: sum(1 for item in candidates if item["article_type"] == article_type) for article_type in ("entity", "concept", "scenario")}
    source_count = len({source for item in candidates for source in item["sources"]})
    report = {"source_count": source_count, "candidate_counts": counts, "intent_count": len(intents), "output": output.relative_to(vault).as_posix()}
    atomic_write(vault / args.report, json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({**report, "report": args.report}))
    return 0




def stage_page_intents(vault: Path, intents_path: Path, stage_dir: str = "_staging", replace: bool = False) -> list[str]:
    staged_root = vault / stage_dir
    outputs: list[str] = []
    for intent in read_jsonl(intents_path):
        target = safe_relative(str(intent.get("target", "")))
        if not target.parts or target.parts[0] not in CATEGORIES:
            raise ValueError(f"intent target must begin with a wiki category: {target}")
        operation = str(intent.get("operation", "create"))
        if operation not in {"create", "patch"}:
            raise ValueError(f"unsupported intent operation: {operation}")
        if operation == "patch" and not target.name.endswith(PATCH_SUFFIX):
            target = target.with_name(target.name + PATCH_SUFFIX)
        citations = tuple(str(item) for item in intent.get("citations", []) if str(item).strip())
        if not citations:
            raise ValueError(f"intent {target}: at least one explicit citation tag is required")
        if operation == "patch" and not str(intent.get("content", "")):
            content = render_patch_intent(intent, target.as_posix())
        elif operation == "create":
            frontmatter = intent.get("frontmatter")
            body = str(intent.get("body", "")).lstrip("\n")
            if not isinstance(frontmatter, dict):
                raise ValueError(f"create intent {target}: frontmatter object required")
            content = render_frontmatter(frontmatter) + "\n" + body.rstrip() + "\n"
            validate_page_content(content, target.as_posix(), patch=False)
        else:
            content = str(intent.get("content", ""))
        missing_citations = [citation for citation in citations if citation not in content]
        if missing_citations:
            raise ValueError(f"intent {target}: citation tags absent from content: {missing_citations}")
        if operation == "patch" and not content:
            content = render_patch_intent(intent, target.as_posix())
            missing_citations = [citation for citation in citations if citation not in content]
            if missing_citations:
                raise ValueError(f"intent {target}: citation tags absent from patch content: {missing_citations}")
        validate_page_content(content, target.as_posix(), patch=operation == "patch")
        output = staged_root / target
        if output.exists() and not replace:
            raise FileExistsError(f"staged target already exists: {output}")
        atomic_write(output, content)
        outputs.append(output.relative_to(vault).as_posix())
    return outputs


def render_frontmatter(values: Mapping[str, Any]) -> str:
    lines = ["---"]
    for key in sorted(values):
        value = values[key]
        if isinstance(value, (list, tuple)):
            if not value:
                lines.append(f"{key}: []")
            elif all(isinstance(item, (str, int, float, bool)) for item in value):
                encoded = ", ".join(json.dumps(item, ensure_ascii=False) for item in value)
                lines.append(f"{key}: [{encoded}]")
            else:
                lines.append(f"{key}:")
                lines.extend(f"  - {json.dumps(item, ensure_ascii=False)}" for item in value)
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for child, child_value in value.items():
                lines.append(f"  {child}: {child_value}")
        else:
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines)


def render_patch_intent(intent: Mapping[str, Any], target: str) -> str:
    frontmatter = dict(intent.get("frontmatter", {}))
    frontmatter.setdefault("target", target)
    frontmatter.setdefault("operation", "patch")
    additions = intent.get("additions", [])
    deletions = intent.get("deletions", [])
    body = [f"# Patch bundle: {target}", "", "## Additions", ""]
    body.extend(f"- {item}" for item in additions)
    body.extend(["", "## Deletions", ""])
    body.extend(f"- {item}" for item in deletions) if deletions else body.append("- None.")
    body.extend(["", "## Citations", ""])
    body.extend(f"- {citation}" for citation in intent.get("citations", []))
    body.extend(["", "## Updated fields", "", "- Fields are supplied in frontmatter.", ""])
    return render_frontmatter(frontmatter) + "\n" + "\n".join(body)


def validate_page_content(content: str, path: str, patch: bool) -> None:
    frontmatter, _ = read_frontmatter(content)
    if not frontmatter:
        raise ValueError(f"{path}: missing frontmatter")
    if patch:
        if not (frontmatter.get("target") or frontmatter.get("patch_target")):
            raise ValueError(f"{path}: patch target missing")
        return
    missing = [key for key in REQUIRED_PAGE_FIELDS if key not in frontmatter]
    if missing:
        raise ValueError(f"{path}: missing required fields {missing}")
    category = Path(path).parts[0]
    expected_type = {"entities": "entity", "concepts": "concept", "scenarios": "scenario", "references": "reference"}.get(category)
    facets = frontmatter.get("facets", {})
    facet_types = facets.get("type", []) if isinstance(facets, dict) else []
    if expected_type and expected_type not in facet_types and not (category == "entities" and any(str(value).startswith("location/") for value in facet_types)):
        raise ValueError(f"{path}: facets.type must include {expected_type!r}")
    tags = frontmatter.get("tags", [])
    if not isinstance(tags, list) or len(tags) > 5:
        raise ValueError(f"{path}: tags must be a list of at most five entries")
    tag_pattern = re.compile(r"^[a-z][a-z0-9-]*(/[a-z0-9-]+)*$")
    if any(not tag_pattern.fullmatch(str(tag)) for tag in tags):
        raise ValueError(f"{path}: tags must be lowercase slash-delimited values")
    summary = str(frontmatter.get("summary", ""))
    if not summary or len(summary) > 200:
        raise ValueError(f"{path}: summary must be present and at most 200 characters")
    if not re.search(r"^provenance:\s*$", content, re.MULTILINE):
        raise ValueError(f"{path}: provenance mapping is required")
    if not re.search(r"^facets:\s*$", content, re.MULTILINE):
        raise ValueError(f"{path}: facets mapping is required")
    relationships = frontmatter.get("relationships", [])
    if isinstance(relationships, list):
        for relation in relationships:
            if isinstance(relation, dict) and relation.get("type") not in ALLOWED_RELATIONSHIPS:
                raise ValueError(f"{path}: unsupported relationship type {relation.get('type')!r}")

def audit_staged(vault: Path, stage_dir: str = "_staging") -> dict[str, Any]:
    root = vault / stage_dir
    problems: list[str] = []
    checked = 0
    for category in sorted(CATEGORIES):
        directory = root / category
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.md")):
            checked += 1
            try:
                validate_page_content(path.read_text(encoding="utf-8"), path.relative_to(root).as_posix(), path.name.endswith(PATCH_SUFFIX))
            except ValueError as error:
                problems.append(str(error))
    return {"checked": checked, "problems": sorted(problems), "ok": not problems}


def _extract_section(text: str, heading: str) -> list[str]:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return []
    end = text.find("\n## ", start + len(marker))
    section = text[start + len(marker) : end if end >= 0 else len(text)]
    return [line[2:].strip() for line in section.splitlines() if line.startswith("- ")]


def _extract_section_replacements(text: str) -> list[tuple[str, str]]:
    marker = "## Section replacements"
    start = text.find(marker)
    if start < 0:
        return []
    section = text[start + len(marker) :]
    matches = re.finditer(r"(?ms)^### Target: ([^\n]+)\n(.*?)(?=^### Target: |^## Citations|^## Updated fields|\Z)", section)
    return [(match.group(1).strip(), match.group(2).strip()) for match in matches]

def apply_patch(target_text: str, patch_text: str) -> str:
    patch_frontmatter, _ = read_frontmatter(patch_text)
    additions = [item for item in _extract_section(patch_text, "Additions") if item.lower() != "none."]
    deletions = [item for item in _extract_section(patch_text, "Deletions") if item.lower() != "none."]
    for deletion in deletions:
        target_text = target_text.replace(deletion + "\n", "")
    for heading, replacement in _extract_section_replacements(patch_text):
        marker = f"## {heading}"
        start = target_text.find(marker)
        if start < 0:
            continue
        end = target_text.find("\n## ", start + len(marker))
        suffix = target_text[end + 1 :] if end >= 0 else ""
        target_text = target_text[:start] + replacement.rstrip() + "\n" + suffix
    if additions:
        insertion = "\n".join(f"- {item}" for item in additions) + "\n"
        source_marker = "\n## Sources"
        position = target_text.find(source_marker)
        if position < 0:
            target_text = target_text.rstrip() + "\n\n" + insertion
        else:
            target_text = target_text[:position] + "\n" + insertion + target_text[position:]
    updated_fields = patch_frontmatter.get("updated_fields", [])
    if isinstance(updated_fields, list):
        for field_name in updated_fields:
            if field_name in patch_frontmatter:
                target_text = replace_frontmatter_field(target_text, str(field_name), patch_frontmatter[field_name])
    return target_text


def replace_frontmatter_field(text: str, key: str, value: Any) -> str:
    if not text.startswith("---\n"):
        raise ValueError("target has no frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError("target frontmatter is unterminated")
    lines = text[4:end].splitlines()
    start = next((index for index, line in enumerate(lines) if line.startswith(f"{key}:")), None)
    if start is None:
        lines.extend(render_frontmatter({key: value}).splitlines()[1:-1])
    else:
        stop = start + 1
        while stop < len(lines) and (lines[stop].startswith(" ") or lines[stop].startswith("-")):
            stop += 1
        replacement = render_frontmatter({key: value}).splitlines()[1:-1]
        lines[start:stop] = replacement
    return "---\n" + "\n".join(lines) + text[end:]


def _validated_archive_entries(vault: Path, manifest_name: str = "_staging/_work/processed_sources.manifest") -> list[tuple[Path, str]]:
    manifest = vault / manifest_name
    if not manifest.exists():
        raise FileNotFoundError(f"processed source manifest missing: {manifest}")
    raw_root = (vault / "_raw").resolve()
    entries: list[tuple[Path, str]] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        fields = line.split("\t")
        source_rel = fields[0]
        source = (vault / safe_relative(source_rel)).resolve()
        if source.parent != raw_root:
            raise ValueError(f"only direct raw children may be archived: {source_rel}")
        if not source.exists():
            raise FileNotFoundError(source)
        if len(fields) > 1 and fields[1] and fields[1] != sha256_file(source):
            raise ValueError(f"hash mismatch before archive: {source_rel}")
        entries.append((source, source_rel))
    return entries


def promote(vault: Path, stage_dir: str = "_staging", confirm: bool = False, archive_raw: bool = False) -> dict[str, Any]:
    if not confirm:
        raise ValueError("promotion is destructive; pass --confirm")
    audit = audit_staged(vault, stage_dir)
    if not audit["ok"]:
        raise ValueError("staged audit failed: " + "; ".join(audit["problems"]))
    archive_entries = _validated_archive_entries(vault) if archive_raw else []
    root = vault / stage_dir
    changes: list[tuple[Path, bytes, bytes | None]] = []
    promoted: list[str] = []
    for category in sorted(CATEGORIES):
        directory = root / category
        if not directory.is_dir():
            continue
        for staged in sorted(directory.rglob("*.md")):
            relative = staged.relative_to(root)
            if staged.name.endswith(PATCH_SUFFIX):
                target_relative = patch_target(staged.read_text(encoding="utf-8"))
                target = vault / safe_relative(target_relative)
                if not target.exists():
                    raise FileNotFoundError(f"patch target does not exist: {target_relative}")
                before = target.read_bytes()
                after = apply_patch(before.decode("utf-8"), staged.read_text(encoding="utf-8")).encode("utf-8")
                changes.append((target, after, before))
                promoted.append(target_relative)
            else:
                target = vault / relative
                if target.exists():
                    raise FileExistsError(f"promotion collision: {target}")
                changes.append((target, staged.read_bytes(), None))
                promoted.append(relative.as_posix())
    written: list[Path] = []
    manifest_path = vault / ".manifest.json"
    manifest_before = manifest_path.read_bytes() if manifest_path.exists() else None
    try:
        for target, after, _ in changes:
            atomic_write(target, after)
            written.append(target)
        update_manifest_after_promotion(vault, stage_dir=stage_dir)
        archived = archive_processed_sources(vault) if archive_raw else []
    except Exception:
        if manifest_before is None:
            manifest_path.unlink(missing_ok=True)
        else:
            atomic_write(manifest_path, manifest_before)
        for target, _, before in changes:
            if target not in written:
                continue
            if before is None:
                target.unlink(missing_ok=True)
            else:
                atomic_write(target, before)
        raise
    receipt = {
        "promoted_at": utc_now(),
        "files": sorted(promoted),
        "archived_sources": archived,
        "archive_preflight_sources": len(archive_entries),
        "staging_preserved": True,
    }
    atomic_write(root / "_work" / "promotion-receipt.json", json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def patch_target(text: str) -> str:
    frontmatter, _ = read_frontmatter(text)
    target = frontmatter.get("target") or frontmatter.get("patch_target")
    if not target:
        raise ValueError("patch target missing")
    return str(target)


def archive_processed_sources(vault: Path, manifest_name: str = "_staging/_work/processed_sources.manifest") -> list[str]:
    entries = _validated_archive_entries(vault, manifest_name)
    raw_root = (vault / "_raw").resolve()
    archive_root = raw_root / "_archived"
    archive_root.mkdir(parents=True, exist_ok=True)
    moved: list[tuple[Path, Path]] = []
    try:
        for source, _ in entries:
            destination = archive_root / source.name
            counter = 1
            while destination.exists():
                destination = archive_root / f"{source.stem}.{counter}{source.suffix}"
                counter += 1
            shutil.move(str(source), str(destination))
            moved.append((source, destination))
    except Exception:
        for source, destination in reversed(moved):
            if destination.exists() and not source.exists():
                shutil.move(str(destination), str(source))
        raise
    return [destination.relative_to(vault).as_posix() for _, destination in moved]

def prepare_processed_manifest(
    vault: Path,
    inventory_path: str = "_staging/_work/inventory.jsonl",
    stage_dir: str = "_staging",
) -> list[str]:
    """Create the archive allow-list only after every inventoried source is covered."""
    inventory = {row["source_rel"]: InventoryRecord(**row) for row in read_jsonl(vault / inventory_path)}
    basename_index: dict[str, list[str]] = {}
    for source_rel in inventory:
        basename_index.setdefault(Path(source_rel).name, []).append(source_rel)
    covered: set[str] = set()
    root = vault / stage_dir
    for category in sorted(CATEGORIES):
        directory = root / category
        if not directory.is_dir():
            continue
        for path in directory.rglob("*.md"):
            frontmatter, _ = read_frontmatter(path.read_text(encoding="utf-8"))
            sources = frontmatter.get("sources", [])
            if isinstance(sources, str):
                sources = [sources]
            for source in sources:
                source_text = str(source)
                if source_text in inventory:
                    covered.add(source_text)
                    continue
                source_name = re.sub(r"^B\d{2}:", "", source_text)
                source_name = Path(source_name).name
                if source_name in basename_index and len(basename_index[source_name]) == 1:
                    covered.add(basename_index[source_name][0])
    missing = sorted(set(inventory) - covered)
    if missing:
        raise ValueError(f"staged outputs do not cover {len(missing)} inventoried sources: {missing[:5]}")
    rows = []
    for source_rel in sorted(inventory):
        path = vault / source_rel
        rows.append(f"{source_rel}\t{sha256_file(path)}\n")
    output = vault / stage_dir / "_work" / "processed_sources.manifest"
    atomic_write(output, "".join(rows))
    return sorted(inventory)

def build_manifest_after_promotion(vault: Path, inventory_path: str = "_staging/_work/inventory.jsonl", stage_dir: str = "_staging") -> dict[str, Any]:
    inventory = {row["source_rel"]: InventoryRecord(**row) for row in read_jsonl(vault / inventory_path)}
    basename_index: dict[str, list[str]] = {}
    for source_rel in inventory:
        basename_index.setdefault(Path(source_rel).name, []).append(source_rel)
    created: dict[str, set[str]] = defaultdict(set)
    updated: dict[str, set[str]] = defaultdict(set)
    root = vault / stage_dir
    for category in sorted(CATEGORIES):
        directory = root / category
        if not directory.is_dir():
            continue
        for path in directory.rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            frontmatter, _ = read_frontmatter(content)
            sources = frontmatter.get("sources", [])
            if isinstance(sources, str):
                sources = [sources]
            target = patch_target(content) if path.name.endswith(PATCH_SUFFIX) else path.relative_to(root).as_posix()
            bucket = updated if path.name.endswith(PATCH_SUFFIX) else created
            for source in sources:
                source_text = str(source)
                if source_text in inventory:
                    source_rel = source_text
                else:
                    source_name = Path(re.sub(r"^B\d{2}:", "", source_text)).name
                    matches = basename_index.get(source_name, [])
                    if len(matches) != 1:
                        continue
                    source_rel = matches[0]
                bucket[source_rel].add(target)
    manifest_path = vault / ".manifest.json"
    existing = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"version": 1, "sources": {}, "stats": {}}
    existing_sources = dict(existing.get("sources", {}))
    entries: dict[str, Any] = {}
    for source_rel, record in sorted(inventory.items()):
        path = vault / source_rel
        source_key = str(path.resolve())
        previous = existing_sources.get(source_key, {})
        suffix = path.suffix.lower()
        source_type = "image" if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"} else "data" if suffix in {".json", ".jsonl", ".csv", ".tsv"} else "document"
        modified_at = (
            datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            if path.exists()
            else str(previous.get("modified_at", utc_now()))
        )
        entries[source_key] = {
            "ingested_at": utc_now(),
            "size_bytes": record.size_bytes,
            "modified_at": modified_at,
            "content_hash": record.content_hash,
            "source_type": source_type,
            "project": previous.get("project"),
            "pages_created": sorted(set(previous.get("pages_created", [])) | created.get(source_rel, set())),
            "pages_updated": sorted(set(previous.get("pages_updated", [])) | updated.get(source_rel, set())),
        }
    existing_sources.update(entries)
    page_count = sum(
        1
        for category in CATEGORIES
        if (vault / category).is_dir()
        for path in (vault / category).rglob("*.md")
        if not path.name.endswith(PATCH_SUFFIX)
    )
    existing["version"] = max(1, int(existing.get("version", 1)))
    existing["sources"] = dict(sorted(existing_sources.items()))
    existing["stats"] = {
        **dict(existing.get("stats", {})),
        "total_sources_ingested": len(existing_sources),
        "total_pages": page_count,
    }
    return existing


def update_manifest_after_promotion(vault: Path, inventory_path: str = "_staging/_work/inventory.jsonl", stage_dir: str = "_staging") -> None:
    atomic_write(vault / ".manifest.json", json.dumps(build_manifest_after_promotion(vault, inventory_path, stage_dir), indent=2, sort_keys=True) + "\n")


def command_prepare_archive(args: argparse.Namespace) -> int:
    sources = prepare_processed_manifest(Path(args.vault).resolve(), args.inventory, args.stage_dir)
    print(json.dumps({"manifest": f"{args.stage_dir}/_work/processed_sources.manifest", "sources": len(sources)}))
    return 0


def command_inventory(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    rows = inventory_sources(vault, args.raw_dir, args.block_size)
    output = vault / args.output
    write_jsonl(output, (row.as_dict() for row in rows))
    print(json.dumps({"sources": len(rows), "output": output.relative_to(vault).as_posix()}))
    return 0


def command_resolve(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    inventory_rows = {row["source_rel"]: InventoryRecord(**row) for row in read_jsonl(vault / args.inventory)}
    mentions = load_candidate_bundles(vault / args.candidates, inventory_rows)
    entities = load_existing_entities(vault)
    result = CanonicalEntityResolver(entities).resolve(mentions)
    atomic_write(vault / args.output, json.dumps(result.as_dict(), indent=2, sort_keys=True) + "\n")
    print(json.dumps({"mentions": len(mentions), "clusters": len(result.clusters), "held": len(result.held)}))
    return 0

def command_stage(args: argparse.Namespace) -> int:
    outputs = stage_page_intents(Path(args.vault).resolve(), Path(args.intents).resolve(), args.stage_dir, args.replace)
    print(json.dumps({"staged": len(outputs), "outputs": outputs}, sort_keys=True))
    return 0


def command_audit(args: argparse.Namespace) -> int:
    result = audit_staged(Path(args.vault).resolve(), args.stage_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


def command_promote(args: argparse.Namespace) -> int:
    result = promote(Path(args.vault).resolve(), args.stage_dir, args.confirm, args.archive_raw)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    inventory = subparsers.add_parser("inventory")
    inventory.add_argument("vault")
    inventory.add_argument("--raw-dir", default="_raw")
    inventory.add_argument("--output", default="_staging/_work/inventory.jsonl")
    inventory.add_argument("--block-size", type=int, default=10)
    inventory.set_defaults(func=command_inventory)
    resolve = subparsers.add_parser("resolve")
    resolve.add_argument("vault")
    resolve.add_argument("--inventory", default="_staging/_work/inventory.jsonl")
    resolve.add_argument("--candidates", default="_staging/_work/candidates")
    resolve.add_argument("--output", default="_staging/_work/resolution.json")
    resolve.set_defaults(func=command_resolve)
    compile_articles = subparsers.add_parser("compile-articles")
    compile_articles.add_argument("vault")
    compile_articles.add_argument("articles")
    compile_articles.add_argument("--output", default="_staging/_work/article-intents.jsonl")
    compile_articles.set_defaults(func=command_compile_articles)
    project_candidates = subparsers.add_parser("project-candidates")
    project_candidates.add_argument("vault")
    project_candidates.add_argument("--candidates", default="_staging/_work/candidates")
    project_candidates.add_argument("--inventory", default="_staging/_work/inventory.jsonl")
    project_candidates.add_argument("--candidate-output", default="_staging/_work/projected-article-candidates.jsonl")
    project_candidates.add_argument("--output", default="_staging/_work/projected-article-intents.jsonl")
    project_candidates.add_argument("--report", default="_staging/_work/projected-article-report.json")
    project_candidates.set_defaults(func=command_project_candidates)
    stage = subparsers.add_parser("stage")
    stage.add_argument("vault")
    stage.add_argument("intents")
    stage.add_argument("--stage-dir", default="_staging")
    stage.add_argument("--replace", action="store_true")
    stage.set_defaults(func=command_stage)
    audit = subparsers.add_parser("audit")
    audit.add_argument("vault")
    audit.add_argument("--stage-dir", default="_staging")
    audit.set_defaults(func=command_audit)
    prepare = subparsers.add_parser("prepare-archive")
    prepare.add_argument("vault")
    prepare.add_argument("--inventory", default="_staging/_work/inventory.jsonl")
    prepare.add_argument("--stage-dir", default="_staging")
    prepare.set_defaults(func=command_prepare_archive)
    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("vault")
    promote_parser.add_argument("--stage-dir", default="_staging")
    promote_parser.add_argument("--confirm", action="store_true")
    promote_parser.add_argument("--archive-raw", action="store_true")
    promote_parser.set_defaults(func=command_promote)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
