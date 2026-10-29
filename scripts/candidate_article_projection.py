from hashlib import sha256

from collections import defaultdict
from pathlib import Path
import re
from typing import Any


STOP_ENTITIES = {
    "rome", "roman empire", "roman republic", "roman world", "roman state",
    "emperor", "magistrates", "senate", "roman senate", "assemblies", "people",
    "authors", "persons", "institutions", "places", "regions", "groups", "concepts",
    "roman army", "roman imperial army", "praetorian prefects",
}
CONCEPT_MARKERS = {
    "concept", "system", "practice", "policy", "institution", "law", "legal",
    "ritual", "process", "authority", "power", "opinion", "traffic", "exile",
    "divination", "frontier", "integration", "memory", "labour", "labor", "religion",
    "architecture", "army", "status", "economy", "knowledge", "identity", "justice",
    "representation", "tradition", "mobility", "citizenship", "property", "voice",
}
SCENARIO_SPECS = (
    ("Crisis Management During the Roman Republic", "Catiline's Emergency Decrees (63 BC)", "Testing republican emergency decision-making through the Catilinarian crisis"),
    ("Cicero, Against Verres", "Verres's Sicilian Extortion Trial", "Testing provincial accountability through Verres's prosecution in Sicily"),
    ("Praetorian", "Praetorian Guard Auction of Empire (193 AD)", "Testing how military privilege can become imperial succession power"),
    ("A History of Exile in the Roman Republic", "Cicero's Voluntary Exile", "Testing exile as a safety valve in late Republican elite conflict"),
    ("Traffic and Congestion in the Roman Empire", "Pompeii Traffic Regulation", "Testing how urban form and traffic rules constrain movement"),
    ("Building the Thermae Agrippae", "Thermae Agrippae Public Bathing Project", "Testing how public bathing infrastructure converts elite resources into civic access"),
    ("Judea Under Roman Domination", "Pompey's Judean Conquest (63 BC)", "Testing the transition from Hasmonean sovereignty to Roman domination"),
    ("Roman Geographies of the Nile", "Agrippa's Roman Geography Program", "Testing how geographic knowledge supports imperial urban ideology"),
    ("Murder Was Not a Crime", "Roman Homicide Prosecution", "Testing how Republican power defined and prosecuted homicide"),
    ("Rome's Enemies Within", "Caesar's Assassination Conspiracy", "Testing how status grievance and constitutional rhetoric combine in a conspiracy"),
)


def _clean_markup(value: str) -> str:
    value = re.sub(r"[`*_]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" .;:-")


def _source_id(block: str, heading: str, inventory: list[dict[str, Any]]) -> tuple[str, str, str]:
    clean_heading = heading.strip().strip("`")
    for row in inventory:
        name = Path(row["source_rel"]).name
        if name == clean_heading or name.lower() == clean_heading.lower():
            return row["source_rel"], row["source_key"], clean_heading
    return f"{block}:{clean_heading}", f"src-{sha256(clean_heading.encode('utf-8')).hexdigest()[:16]}", clean_heading


def _field(lines: list[str], markers: tuple[str, ...]) -> str:
    for index, line in enumerate(lines):
        lower = line.lower()
        if any(marker in lower for marker in markers) and ":" in line:
            value = line.split(":", 1)[1].strip()
            parts = [value] if value else []
            for continuation in lines[index + 1:]:
                if re.match(r"^-\s*(?:\*{0,2})?(?:candidate\s+)?(?:entities|relationships|proposed facets|facets|open ambiguities|ambiguities|status|key claims|sampled claims)\b", continuation, re.I):
                    break
                if continuation.strip():
                    parts.append(continuation.strip())
            return " ".join(parts).strip()
    return ""


def _claims(lines: list[str]) -> list[str]:
    raw = _field(lines, ("key claims", "sampled claims", "bounded claims"))
    if not raw:
        return []
    chunks = re.split(r"(?=(?:\(\d+\)|\d+\.)\s*)", raw)
    if len(chunks) == 1:
        chunks = re.split(r"\s+-\s+", raw)
    result = []
    for chunk in chunks:
        clean = _clean_markup(re.sub(r"^\(?\d+\)?[.:]?\s*", "", chunk))
        if len(clean) >= 20:
            result.append(clean)
    return result


def _chunks(value: str) -> list[str]:
    return [chunk.strip() for chunk in re.split(r";\s+", value) if chunk.strip()]


def _entity_name(chunk: str) -> tuple[str, str]:
    clean = _clean_markup(chunk)
    name = re.split(r"\s+[—–]\s+|\s+\(|\s+→", clean, maxsplit=1)[0].strip()
    descriptor = clean[len(name):].strip(" -—–:")
    return _clean_markup(name), descriptor


def _facets(value: str) -> dict[str, list[str]]:
    result = {key: [] for key in ("domain", "type", "period", "place", "material", "subject")}
    lower = value.lower()
    ignored = {"type", "period", "place", "domain", "material", "subject", "only", "where", "explicitly", "broad", "scope", "not", "assigned", "proposed", "central", "tentative", "none", "avoid"}
    for key in result:
        slash_values = re.findall(rf"{key}/([a-z][a-z-]+)", lower)
        colon = re.search(rf"{key}\s*:\s*([^;]+)", lower)
        colon_values = re.findall(r"[a-z][a-z-]+", colon.group(1)) if colon else []
        result[key] = sorted({item for item in slash_values + colon_values if item not in ignored})
    return result


def _parse_sections(candidates_dir: Path, inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    for path in sorted(candidates_dir.glob("B*.md")):
        text = path.read_text(encoding="utf-8")
        block = re.search(r"^block:\s*(\S+)", text, re.M)
        block_name = block.group(1) if block else path.stem
        pieces = re.split(r"^##\s+", text, flags=re.M)
        for piece in pieces[1:]:
            heading, _, body = piece.partition("\n")
            source_rel, source_key, clean_heading = _source_id(block_name, heading, inventory)
            lines = body.splitlines()
            title_line = _field(lines, ("title/author", "title / author", "title/editors"))
            title = _clean_markup(title_line.split("—", 1)[0] if title_line else clean_heading)
            entity_value = _field(lines, ("candidate entities", "entities (", "entities:"))
            relationship_value = _field(lines, ("candidate relationships", "bounded relationships", "relationships:"))
            facet_value = _field(lines, ("proposed facets", "facets:"))
            sections.append({
                "block": block_name,
                "heading": clean_heading,
                "source_rel": source_rel,
                "source_key": source_key,
                "source_title": title,
                "claims": _claims(lines),
                "entities": [_entity_name(chunk) for chunk in _chunks(entity_value)],
                "relationships": relationship_value,
                "facets": _facets(facet_value),
                "ambiguities": _field(lines, ("open ambiguities", "ambiguities:")),
            })
    return sections


def _valid_candidate_name(name: str) -> bool:
    normalized = name.lower().strip()
    words = normalized.split()
    if not normalized or normalized[0].isdigit() or len(words) > 5:
        return False
    if any(token in normalized for token in ("relationships", "proposed facets", "open ambiguities", "domain legal", "domain political", "chapter")):
        return False
    if normalized.count(",") > 1 or "→" in normalized:
        return False
    return True


def _entity_quality(name: str, descriptor: str) -> bool:
    normalized = name.lower()
    if not _valid_candidate_name(name) or normalized in STOP_ENTITIES or len(normalized) < 3:
        return False
    descriptor_lower = descriptor.lower()
    return any(marker in descriptor_lower for marker in ("person", "author", "editor", "emperor", "king", "official", "institution", "building", "monument", "location", "law", "army", "guard", "road", "aqueduct", "city", "scholar", "group", "deity", "jurist", "governor"))


def _concept_quality(name: str, descriptor: str) -> bool:
    normalized = name.lower()
    if not _valid_candidate_name(name) or normalized in STOP_ENTITIES or len(normalized) < 4:
        return False
    text = f"{normalized} {descriptor.lower()}"
    return any(marker in text for marker in CONCEPT_MARKERS)


def _existing_paths(vault: Path) -> tuple[set[str], set[str]]:
    paths = {path.relative_to(vault).with_suffix("").as_posix() for category in ("entities", "concepts", "scenarios", "references") if (vault / category).is_dir() for path in (vault / category).rglob("*.md") if not path.name.endswith(".patch.md")}
    return paths, {path.rsplit("/", 1)[-1] for path in paths}




def _slug(value: str) -> str:
    value = value.lower().replace("'", "")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    tokens = [token for token in value.split("-") if token != "and"]
    return "-".join(tokens)


def _tags(facets: dict[str, list[str]], article_type: str) -> list[str]:
    tags = [f"type/{article_type}"]
    for key in ("domain", "period", "material", "subject"):
        for value in facets.get(key, []):
            tags.append(f"{key}/{value}")
            if len(tags) == 5:
                return sorted(set(tags))
    return sorted(set(tags))


def _paragraphs_for(name: str, evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    paragraphs: list[dict[str, Any]] = []
    tokens = [token for token in re.findall(r"[a-zA-Z]{4,}", name.lower()) if token not in {"roman", "imperial", "republican"}]
    for item in evidence:
        selected = [claim for claim in item["claims"] if not tokens or any(token in claim.lower() for token in tokens)]
        if not selected:
            selected = item["claims"][:1]
        for claim in selected[:2]:
            paragraphs.append({"text": claim, "citation": f"^{item['source_key'].removeprefix('src-')}", "source": item["source_rel"]})
    return paragraphs


def build_article_candidates(vault: Path, candidates_dir: Path, inventory_path: str = "_staging/_work/inventory.jsonl") -> list[dict[str, Any]]:
    import json
    inventory = [json.loads(line) for line in (vault / inventory_path).read_text(encoding="utf-8").splitlines() if line.strip()]
    sections = _parse_sections(candidates_dir, inventory)
    existing, existing_slugs = _existing_paths(vault)
    by_entity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    descriptors: dict[str, str] = {}
    for section in sections:
        for name, descriptor in section["entities"]:
            key = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
            if _entity_quality(name, descriptor):
                by_entity[key].append(section)
                descriptors.setdefault(key, descriptor)
    records: list[dict[str, Any]] = []
    generated_targets: dict[str, str] = {}
    for key, evidence in sorted(by_entity.items(), key=lambda pair: (-len({item['source_rel'] for item in pair[1]}), pair[0]))[:60]:
        name = next(name for section in evidence for name, _ in section["entities"] if re.sub(r"[^a-z0-9]+", " ", name.lower()).strip() == key)
        target = f"entities/{_slug(name)}"
        if target in existing or _slug(name) in existing_slugs or not _slug(name):
            continue
        existing_slugs.add(_slug(name))
        generated_targets.setdefault(evidence[0]["source_rel"], target)
        facet_values = {facet: sorted(set(value for item in evidence for value in item["facets"].get(facet, []))) for facet in ("domain", "period", "place", "material", "subject")}
        paragraphs = _paragraphs_for(name, evidence)
        citations = sorted({f"^{item['source_key'].removeprefix('src-')}" for item in evidence})
        records.append({
            "article_type": "entity", "title": name, "focus": f"The identity, role, and source evidence for {name}",
            "sources": [f"{item['block']}:{item['heading']}" for item in evidence], "citations": citations,
            "summary": f"Source-grounded evidence for {name} in the Roman historical record.", "tags": _tags(facet_values, "entity"),
            "facets": {**facet_values, "type": ["entity"]},
            "links": ["concepts/fall-of-the-roman-republic", "concepts/roman-law-and-trials"],
            "sections": [{"heading": "Evidence", "paragraphs": [f"{paragraph['text']} {paragraph['citation']}" for paragraph in paragraphs]}, {"heading": "Boundary", "paragraphs": [f"This page consolidates sampled mentions of {name}; it does not infer a complete biography or institutional history from those mentions."]}],
        })
    by_concept: dict[str, list[dict[str, Any]]] = defaultdict(list)
    concept_names: dict[str, str] = {}
    for section in sections:
        for name, descriptor in section["entities"]:
            if _concept_quality(name, descriptor):
                key = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
                by_concept[key].append(section)
                concept_names.setdefault(key, name)
    for key, evidence in sorted(by_concept.items(), key=lambda pair: (-len({item['source_rel'] for item in pair[1]}), pair[0]))[:45]:
        name = concept_names[key]
        target = f"concepts/{_slug(name)}"
        if target in existing or _slug(name) in existing_slugs or not _slug(name):
            continue
        existing_slugs.add(_slug(name))
        facet_values = {facet: sorted(set(value for item in evidence for value in item["facets"].get(facet, []))) for facet in ("domain", "period", "place", "material", "subject")}
        paragraphs = _paragraphs_for(name, evidence)
        citations = sorted({f"^{item['source_key'].removeprefix('src-')}" for item in evidence})
        records.append({
            "article_type": "concept", "title": name, "focus": f"The bounded meaning and operation of {name} in the sampled Roman sources",
            "sources": [f"{item['block']}:{item['heading']}" for item in evidence], "citations": citations,
            "summary": f"A bounded account of {name} in Roman history.", "tags": _tags(facet_values, "concept"),
            "facets": {**facet_values, "type": ["concept"]},
            "links": ["concepts/fall-of-the-roman-republic", "concepts/roman-religion-and-augury"],
            "sections": [{"heading": "Core Evidence", "paragraphs": [f"{paragraph['text']} {paragraph['citation']}" for paragraph in paragraphs]}, {"heading": "Boundary", "paragraphs": [f"This page treats {name} as a bounded analytical subject and does not generalize across unrelated periods or institutions."]}],
        })
    for source_match, title, focus in SCENARIO_SPECS:
        evidence = [item for item in sections if source_match.lower() in item["heading"].lower()]
        if not evidence:
            continue
        item = evidence[0]
        target = f"scenarios/{_slug(title)}"
        if target in existing:
            continue
        paragraphs = item["claims"][:3] or [f"The candidate source identifies {title} as a case requiring focused analysis."]
        citation = f"^{item['source_key'].removeprefix('src-')}"
        facets = {facet: sorted(set(item["facets"].get(facet, []))) for facet in ("domain", "period", "place", "material", "subject")}
        records.append({
            "article_type": "scenario", "title": title, "focus": focus,
            "sources": [f"{item['block']}:{item['heading']}"], "citations": [citation],
            "summary": f"A focused scenario for {focus[:1].lower() + focus[1:]}.", "tags": _tags(facets, "scenario"),
            "facets": {**facets, "type": ["scenario"]}, "links": ["concepts/fall-of-the-roman-republic", "concepts/senatus-consultum-ultimum"],
            "sections": [{"heading": "Scenario Evidence", "paragraphs": [f"{claim} {citation}" for claim in paragraphs]}, {"heading": "Decision Boundary", "paragraphs": [f"The scenario isolates {focus.lower()} and does not stand in for the source's entire historical argument."]}],
        })
    return records
