"""Prepare source-grounded enrichment packets for evidence-only articles.

This command does not invent propositions. It retrieves source passages for each
article, preserving source boundaries, so a later writer can assert only claims
supported by the raw text and cite the returned locators.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re

try:
    from .raw_source_search import search
except ImportError:
    from raw_source_search import search


def frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    result = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("["):
            try:
                result[key] = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                result[key] = []
        else:
            result[key] = value.strip('"')
    return result


def inventory_source_map(vault: Path, inventory_path: str) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for line in (vault / inventory_path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        source_rel = str(row["source_rel"])
        label = f"{row.get('block', '')}:{Path(source_rel).name}"
        mapping.setdefault(label, []).append(source_rel)
        mapping.setdefault(Path(source_rel).name, []).append(source_rel)
    return mapping


def source_paths(labels: list[str], mapping: dict[str, list[str]]) -> list[str]:
    result: list[str] = []
    for label in labels:
        key = label.split(":", 1)[-1] if ":" in label else label
        for path in mapping.get(label, []) + mapping.get(key, []):
            if path not in result:
                result.append(path)
    return result


def query_for(title: str, scope: str, evidence: str = "") -> str:
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", f"{title} {scope} {evidence}")
    stop = {"the", "and", "for", "from", "roman", "source", "evidence", "history", "historical", "identity", "role"}
    unique = []
    for word in words:
        lowered = word.lower()
        if len(lowered) < 5 or lowered in stop or lowered in unique:
            continue
        unique.append(lowered)
    return " ".join(unique[:18])


def collect_packets(vault: Path, db_path: Path, inventory_path: str, page_globs: list[str], limit: int) -> list[dict]:
    mapping = inventory_source_map(vault, inventory_path)
    packets = []
    for pattern in page_globs:
        for page in sorted(vault.glob(pattern)):
            text = page.read_text(encoding="utf-8")
            fm = frontmatter(text)
            if not fm:
                continue
            headings = [line[3:].strip().lower() for line in text.splitlines() if line.startswith("## ")]
            has_evidence = any("evidence" in heading for heading in headings)
            assertion_terms = ("proposition", "claim", "description", "overview", "argument", "finding", "interpretation", "analysis")
            if not has_evidence or any(any(term in heading for term in assertion_terms) for heading in headings):
                continue
            evidence_match = re.search(r"(?ms)^## [^\n]*evidence[^\n]*\n(.*?)(?=^## |\Z)", text, re.I)
            evidence = evidence_match.group(1) if evidence_match else ""
            labels = fm.get("sources", []) if isinstance(fm.get("sources", []), list) else []
            paths = source_paths([str(label) for label in labels], mapping)
            query = query_for(str(fm.get("title", page.stem)), str(fm.get("scope", "")), evidence)
            title_terms = " ".join(word.lower() for word in re.findall(r"[A-Za-z][A-Za-z'-]+", str(fm.get("title", ""))) if len(word) >= 5)
            primary = search(db_path, title_terms, limit=limit, sources=paths or None) if title_terms else []
            secondary = search(db_path, query, limit=limit, sources=paths or None)
            primary_keys = {(item["source"], item["locator"]) for item in primary}
            passages = primary + [item for item in secondary if (item["source"], item["locator"]) not in primary_keys]
            packets.append({
                "page": page.relative_to(vault).as_posix(),
                "title": fm.get("title", page.stem),
                "scope": fm.get("scope", ""),
                "source_labels": labels,
                "source_paths": paths,
                "query": query,
                "passages": passages,
                "required_output": [
                    "Write 2-4 explicit propositions, each stating a defensible claim.",
                    "Attach a raw-source locator to every proposition.",
                    "Separate extracted claims from inference and state evidentiary limits.",
                    "Do not preserve the evidence dump as the article's main section.",
                ],
            })
    return packets

def _proposition_sentences(packet: dict, limit: int = 3) -> list[tuple[str, str, str]]:
    seen = set()
    locator_counts = {}
    selected = []
    title_anchors = {word.lower() for word in re.findall(r"[A-Za-z][A-Za-z'-]+", str(packet.get("title", ""))) if len(word) >= 5}
    query_anchors = {word.lower() for word in re.findall(r"[A-Za-z][A-Za-z'-]+", str(packet.get("query", ""))) if len(word) >= 5}
    anchors = title_anchors or query_anchors
    noise = ("bibliograph", "isbn", "see on", "nr.", "paris:", "cambridge:", "oxford:", "contents", "plates and maps", "copyright", "appendix", "select bibliography", "catalogue record", "all photographs", "q.v.", "run-up", "the trial of verres")
    verbs = (" is ", " are ", " was ", " were ", " has ", " have ", " had ", " argues ", " shows ", " treats ", " indicates ", " suggests ", " concerns ", " describes ", " links ", " shapes ", " became ", " addressed ", " said ", " means ", " requires ")
    for passage in packet.get("passages", []):
        text = re.sub(r"(?<=\w)-\s+(?=\w)", "", re.sub(r"\s+", " ", str(passage.get("text") or passage.get("snippet", ""))).strip())
        source = str(passage["source"])
        locator = str(passage["locator"])
        if locator_counts.get(locator, 0) >= 2:
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            sentence = sentence.strip(" -")
            lower = sentence.lower()
            if len(sentence) < 55 or len(sentence) > 420:
                continue
            if any(token in lower for token in noise):
                continue
            if anchors and not any(anchor in lower for anchor in anchors):
                continue
            if not any(verb in f" {lower} " for verb in verbs):
                continue
            if re.match(r"^(?:\d+|[A-Z][A-Za-z-]+,\s+[A-Z])", sentence) and not any(verb in lower for verb in (" is ", " are ", " was ", " were ", " argues ", " shows ", " treats ")):
                continue
            key = re.sub(r"[^a-z0-9]+", " ", lower).strip()
            if key in seen:
                continue
            seen.add(key)
            locator_counts[locator] = locator_counts.get(locator, 0) + 1
            selected.append((sentence, source, locator))
            if len(selected) == limit:
                return selected
        if len(selected) == limit:
            return selected
    return selected


def _marker(source: str, locator: str) -> str:
    import hashlib
    return "^raw-" + hashlib.sha256(f"{source}#{locator}".encode("utf-8")).hexdigest()[:12]


def hydration_intents(vault: Path, packets_path: Path) -> list[dict]:
    packets = [json.loads(line) for line in packets_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    intents = []
    for packet in packets:
        selected = _proposition_sentences(packet)
        if len(selected) < 2:
            continue
        propositions = [
            f"{sentence} (source: {source}; {locator}) {_marker(source, locator)}"
            for sentence, source, locator in selected
        ]
        notes = [
            f"{source} — {locator} {_marker(source, locator)}"
            for _, source, locator in selected
        ]
        replacement = "## Propositions\n\n" + "\n".join(f"- {item}" for item in propositions)
        replacement += "\n\n## Evidence Notes\n\n" + "\n".join(f"- {item}" for item in notes)
        citations = [_marker(source, locator) for _, source, locator in selected]
        target = packet["page"]
        target_text = (vault / target).read_text(encoding="utf-8")
        heading_match = re.search(r"^## ([^\n]*evidence[^\n]*)$", target_text, re.I | re.M)
        evidence_heading = heading_match.group(1).strip() if heading_match else "Evidence"
        frontmatter = (
            "---\n"
            "operation: patch\n"
            f"target: {json.dumps(target)}\n"
            "updated_fields:\n"
            '  - "updated"\n'
            'updated: "2026-10-29T20:13:43Z"\n'
            "hydration: proposition-pass\n"
            "---\n"
        )
        body = [
            f"# Hydration patch: {target}",
            "",
            "## Additions",
            "",
            "- None.",
            "",
            "## Deletions",
            "",
            "- None.",
            "",
            "## Section replacements",
            "",
            f"### Target: {evidence_heading}",
            replacement,
            "",
            "## Citations",
            "",
            *[f"- {citation}" for citation in citations],
            "",
            "## Updated fields",
            "",
            "- updated",
            "",
        ]
        intents.append({"target": target, "operation": "patch", "citations": citations, "content": frontmatter + "\n".join(body)})
    return intents


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault")
    parser.add_argument("--db", default="_staging/_work/raw-search.sqlite3")
    parser.add_argument("--inventory", default="_staging/_work/inventory.jsonl")
    parser.add_argument("--output", default="_staging/_work/article-enrichment-packets.jsonl")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--pages", nargs="*", default=["entities/quarantine/*.md", "concepts/*.md", "scenarios/*.md"])
    parser.add_argument("--hydration-output", default="")
    args = parser.parse_args()
    vault = Path(args.vault).resolve()
    packets = collect_packets(vault, vault / args.db, args.inventory, args.pages, args.limit)
    output = vault / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(packet, ensure_ascii=False, sort_keys=True) + "\n" for packet in packets), encoding="utf-8")
    result = {"packets": len(packets), "with_passages": sum(bool(p["passages"]) for p in packets), "output": output.relative_to(vault).as_posix()}
    if args.hydration_output:
        hydration_path = vault / args.hydration_output
        intents = hydration_intents(vault, output)
        hydration_path.parent.mkdir(parents=True, exist_ok=True)
        hydration_path.write_text("".join(json.dumps(intent, ensure_ascii=False, sort_keys=True) + "\n" for intent in intents), encoding="utf-8")
        result.update({"hydration_intents": len(intents), "hydration_output": hydration_path.relative_to(vault).as_posix()})
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
