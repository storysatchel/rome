"""Build and query a local full-text index over archived ingestion sources.

The ingest manifest retains logical paths such as ``_raw/example.pdf`` after
promotion archives the bytes under ``_raw/_archived``.  This module resolves
those logical paths, extracts text locally, stores page/section chunks in
SQLite FTS5, and returns source-located passages for a later proposition pass.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import html
import json
import re
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

SUPPORTED = {".pdf", ".epub", ".txt", ".md"}


@dataclass(frozen=True)
class Source:
    logical_path: str
    physical_path: Path
    content_hash: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_inventory(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def resolve_source(vault: Path, logical_path: str) -> Path:
    direct = vault / logical_path
    if direct.is_file():
        return direct
    archived = vault / "_raw" / "_archived" / Path(logical_path).name
    if archived.is_file():
        return archived
    raise FileNotFoundError(f"source bytes not found for {logical_path}")


def discover_sources(vault: Path, inventory_path: str = "_staging/_work/inventory.jsonl") -> list[Source]:
    records = read_inventory(vault / inventory_path)
    sources = []
    for record in records:
        logical = str(record["source_rel"])
        physical = resolve_source(vault, logical)
        digest = sha256_file(physical)
        expected = str(record.get("content_hash", "")).removeprefix("sha256:")
        if expected and digest != expected:
            raise ValueError(f"hash mismatch for {logical}: {physical}")
        sources.append(Source(logical, physical, digest))
    return sources


def _extract_epub(path: Path) -> str:
    if not shutil.which("ebook-convert"):
        raise RuntimeError("ebook-convert is required to index EPUB sources")
    with tempfile.TemporaryDirectory(prefix="rome-epub-") as temp:
        output = Path(temp) / "source.txt"
        subprocess.run(["ebook-convert", str(path), str(output)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.read_text(encoding="utf-8", errors="replace")


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        if not shutil.which("pdftotext"):
            raise RuntimeError("pdftotext is required to index PDF sources")
        result = subprocess.run(["pdftotext", "-raw", "-enc", "UTF-8", str(path), "-"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode("utf-8", errors="replace")
    if suffix == ".epub":
        return _extract_epub(path)
    raise ValueError(f"unsupported source type: {path}")


def _clean(text: str) -> str:
    text = html.unescape(text).replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def chunk_text(text: str, suffix: str) -> Iterable[tuple[str, str]]:
    pages = text.split("\f") if suffix == ".pdf" else [text]
    for page_number, page in enumerate(pages, 1):
        paragraphs = [p for p in re.split(r"\n\s*\n", page) if _clean(p)]
        if not paragraphs:
            continue
        buffer: list[str] = []
        size = 0
        chunk_number = 1
        for paragraph in paragraphs:
            clean = _clean(paragraph)
            if not clean:
                continue
            if buffer and size + len(clean) > 2400:
                yield f"p.{page_number}.{chunk_number}" if suffix == ".pdf" else f"section.{chunk_number}", "\n\n".join(buffer)
                buffer, size = [], 0
                chunk_number += 1
            buffer.append(clean)
            size += len(clean) + 2
        if buffer:
            yield f"p.{page_number}.{chunk_number}" if suffix == ".pdf" else f"section.{chunk_number}", "\n\n".join(buffer)


def open_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("CREATE TABLE IF NOT EXISTS sources (logical_path TEXT PRIMARY KEY, physical_path TEXT NOT NULL, content_hash TEXT NOT NULL, indexed_at TEXT NOT NULL)")
    db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(logical_path UNINDEXED, locator UNINDEXED, text, tokenize='unicode61')")
    return db


def build_index(vault: Path, db_path: Path, inventory_path: str = "_staging/_work/inventory.jsonl") -> dict:
    sources = discover_sources(vault, inventory_path)
    db = open_db(db_path)
    indexed = 0
    chunks = 0
    for source in sources:
        row = db.execute("SELECT content_hash FROM sources WHERE logical_path = ?", (source.logical_path,)).fetchone()
        if row and row[0] == source.content_hash:
            continue
        db.execute("DELETE FROM chunks WHERE logical_path = ?", (source.logical_path,))
        text = extract_text(source.physical_path)
        for locator, chunk in chunk_text(text, source.physical_path.suffix.lower()):
            db.execute("INSERT INTO chunks(logical_path, locator, text) VALUES (?, ?, ?)", (source.logical_path, locator, chunk))
            chunks += 1
        db.execute("INSERT OR REPLACE INTO sources(logical_path, physical_path, content_hash, indexed_at) VALUES (?, ?, ?, datetime('now'))", (source.logical_path, str(source.physical_path), source.content_hash))
        indexed += 1
        db.commit()
    total = db.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    total_chunks = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    db.close()
    return {"sources_seen": len(sources), "sources_indexed": indexed, "sources_cached": total, "chunks": total_chunks}


def _match_query(query: str) -> str:
    terms = re.findall(r"[\w-]+", query.lower(), re.UNICODE)
    if not terms:
        raise ValueError("query must contain at least one word")
    return " OR ".join(f'"{term.replace(chr(34), "")}"' for term in terms)


def search(db_path: Path, query: str, limit: int = 10, sources: Iterable[str] | None = None) -> list[dict]:
    db = sqlite3.connect(db_path)
    match = _match_query(query)
    clauses = ["chunks MATCH ?"]
    params: list[object] = [match]
    source_list = list(sources or [])
    if source_list:
        placeholders = ", ".join("?" for _ in source_list)
        clauses.append(f"logical_path IN ({placeholders})")
        params.extend(source_list)
    params.append(limit)
    rows = db.execute(f"SELECT logical_path, locator, text, snippet(chunks, 2, '[', ']', ' … ', 42), bm25(chunks) FROM chunks WHERE {' AND '.join(clauses)} ORDER BY bm25(chunks) LIMIT ?", params).fetchall()
    db.close()
    return [{"source": row[0], "locator": row[1], "text": row[2], "snippet": row[3], "score": row[4]} for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    index = sub.add_parser("index")
    index.add_argument("vault")
    index.add_argument("--inventory", default="_staging/_work/inventory.jsonl")
    index.add_argument("--db", default="_staging/_work/raw-search.sqlite3")
    query = sub.add_parser("search")
    query.add_argument("vault")
    query.add_argument("query")
    query.add_argument("--db", default="_staging/_work/raw-search.sqlite3")
    query.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    vault = Path(args.vault).resolve()
    db = vault / args.db
    if args.command == "index":
        print(json.dumps(build_index(vault, db, args.inventory), sort_keys=True))
    else:
        print(json.dumps(search(db, args.query, args.limit), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
