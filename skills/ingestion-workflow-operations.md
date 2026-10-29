---
title: Vault Ingestion Workflow Operations
category: skills
tags: [type/metadata, subject/ingest-pipeline]
sources: ["@/home/user/Downloads/vault_ingestion_architecture_entity_resolution_workflow.md"]
summary: Operational contract for deterministic entity resolution, staged Markdown integration, audit gates, promotion, and hash-checked raw-source archiving.
provenance:
  extracted: 0.75
  inferred: 0.20
  ambiguous: 0.05
base_confidence: 0.57
lifecycle: draft
lifecycle_changed: "2026-10-29"
created: "2026-10-29T00:00:00Z"
updated: "2026-10-29T00:00:00Z"
facets:
  domain: []
  type: [reference]
  period: []
  place: []
  material: []
  subject: [ingest-pipeline]
---

# Vault ingestion workflow

`entity_resolution_engine.py` and `ingest_workflow.py` implement the staged ingestion boundary described in `vault_ingestion_architecture_entity_resolution_workflow.md`.

## Safety model

- Extraction workers write one JSON candidate bundle per source. The coordinator never treats a filename as an entity identity and never extracts claims from a filename.
- Inventory, candidate bundles, resolution output, intents, audit results, and promotion receipts are deterministic artifacts.
- Parallel work is safe before reconciliation. Resolution is a global barrier; Markdown integration is grouped by exact target path.
- The repository uses `_staging/` (not `_staged/`) because `WIKI_STAGED_WRITES=true` is enabled. `_staging/_work/` and `_staging/_meta/` are control artifacts and are never promoted.
- Promotion requires both a clean staged audit and `--confirm`. Raw files are never archived unless `--archive-raw` is explicitly supplied with a hash-checked `processed_sources.manifest`.
- Promotion leaves staged artifacts in place and writes `_staging/_work/promotion-receipt.json`; this preserves rollback evidence and prevents accidental double-processing.

## Commands

Run from the repository root:

```bash
python3 scripts/ingest_workflow.py inventory /home/user/Documents/rome
python3 scripts/ingest_workflow.py resolve /home/user/Documents/rome \
  --inventory _staging/_work/inventory.jsonl \
  --candidates _staging/_work/candidates
python3 scripts/ingest_workflow.py stage /home/user/Documents/rome intents.jsonl
python3 scripts/ingest_workflow.py audit /home/user/Documents/rome
python3 scripts/ingest_workflow.py prepare-archive /home/user/Documents/rome
python3 scripts/ingest_workflow.py promote /home/user/Documents/rome --confirm --archive-raw
```


## Raw-source retrieval for enrichment

Promotion does not make source text searchable. The inventory's logical paths remain valid after raw files move to `_raw/_archived/`; build a local SQLite FTS5 index before enriching evidence-only pages:

```bash
python3 scripts/raw_source_search.py index /home/user/Documents/rome
python3 scripts/raw_source_search.py search /home/user/Documents/rome \
  "annona grain distribution imperial politics" --limit 8
```

The index resolves each inventory path against `_raw/` and `_raw/_archived/`, verifies the inventory SHA-256, extracts PDF/EPUB/TXT content locally, and stores page- or section-located chunks under `_staging/_work/raw-search.sqlite3`. It is a retrieval layer, not an article writer.

Generate retrieval packets for the quarantined entities and evidence-only concepts/scenarios:

```bash
python3 scripts/article_enrichment.py /home/user/Documents/rome \
  --limit 24 \
  --output _staging/_work/article-enrichment-packets.jsonl \
  --hydration-output _staging/_work/article-hydration-intents.jsonl
```

The hydration output is an extraction intermediate, not a publishable article. Sentence matching cannot establish referents, narrative coherence, or historical significance. Read the surrounding passages, resolve the subject of every assertion, and synthesize a cohesive article before writing it to the live vault.

Enrichment requires renewed research, not just an editorial pass over existing excerpts. Search the full raw corpus for the article subject, read the relevant surrounding pages or sections, and identify missing mechanisms, chronology, examples, and competing interpretations before composing. Record the actual ranges consulted and source limitations in the work audit. Citation presence and fluent prose alone do not demonstrate research coverage.

### Article presentation

- With `WIKI_STAGED_WRITES=false`, write directly to the normal category paths. Git provides review and rollback; do not introduce a separate promotion gate.
- Open with a useful description of the subject, then use headings specific to its history, function, or argument.
- Write connected prose. Do not publish a literal “Propositions” section, a list of retrieved quotations, or generic Scope/Boundary boilerplate.
- Keep source paths, page locators, and extraction markers out of the narrative. Consolidate precise source attribution into compact notes under `## Sources`; use unobtrusive footnotes only when a claim needs distinct attribution.
- Apply subject-first prose to every article, not just new or recently enriched pages. Keep routine modern scholarly attribution in source notes rather than narrating “X argues,” “Y agrees with Z,” or “the source describes.” State the substantive interpretation directly and retain its uncertainty: disputed chronology stays disputed, alternative reconstructions stay alternatives, and allegations do not become facts. Source notes must identify which interpretation each source supports when accounts differ. Bibliographic identity and authorship remain explicit in articles actually about a book or scholar; ancient testimony stays distinguishable from established events.
- Retain source identity and page/section locators. Do not count alternate PDF/EPUB encodings as independent corroboration.
- Omit unsupported claims rather than padding an article. An unresolved pronoun or a sentence about another person is not evidence about the page subject.

Add `--archive-raw` only after the processed-source manifest has one exact raw-relative path and matching SHA-256 per source:

```text
_raw/example.pdf\t<64 lowercase hexadecimal SHA-256>
```

The archive operation accepts only direct children of `_raw/`, verifies the hash, preserves filename collisions with a numeric suffix, and moves one exact path at a time.

## Candidate bundle contract

Each file in the candidates directory is a JSON object with exactly one source identity and a list of mentions:

```json
{
  "source_rel": "_raw/example.pdf",
  "mentions": [
    {
      "name": "Thermae Agrippae",
      "entity_type": "building",
      "aliases": ["Baths of Agrippa"],
      "period": ["principate"],
      "place": ["rome"],
      "stable_ids": [],
      "tags": ["type/location/building"],
      "evidence": ["p. 14"]
    }
  ]
}
```

Candidate files are source-isolated. Duplicate bundles for one source or a source absent from inventory abort resolution.

## Entity resolution rules

1. Normalize only for comparison; preserve source spelling in evidence.
2. Block by normalized stem, explicit type, period, place, taxonomy facet, and stable identifiers.
3. Resolve exact names and alias intersections only when type, stable identifiers, period, and place do not conflict.
4. Run the stable-identifier and exact-name bridge pass after intra-block Union-Find matching.
5. Ground only against existing page title/aliases with compatible context. Generic homonyms remain held instead of being merged.
6. MurmurHash3 x86/32 assigns block keys to workers reproducibly; worker count changes scheduling, not identity decisions.

## Page contracts

### Typed article projection

Reference extraction is not the only output. High-value article candidates can be compiled into first-class `entities/`, `concepts/`, and `scenarios/` pages without bypassing the same staging and audit boundary.

Create one JSON object per article candidate:

```json
{
  "article_type": "concept",
  "title": "Divinatory Authorization in Late Republican Rome",
  "focus": "How signs authorized or contested political action during the late Republic",
  "sources": ["B03:divination-republic.pdf"],
  "citations": ["^src-divination-republic"],
  "summary": "How divinatory signs authorized or contested political action in late Republican Rome.",
  "tags": ["domain/political", "subject/roman-religion"],
  "links": ["concepts/roman-religion-and-augury", "references/divination-prediction-end-roman-republic-federico-santangelo"],
  "facets": {
    "domain": ["political"],
    "type": ["concept"],
    "period": ["late-republic"],
    "place": ["rome"],
    "material": [],
    "subject": ["roman-religion", "augury"]
  },
  "sections": [
    {
      "heading": "Core Mechanism",
      "paragraphs": ["Signs framed political uncertainty by authorizing, delaying, or challenging action. ^src-divination-republic"]
    },
    {
      "heading": "Boundary",
      "paragraphs": ["The page treats divination as a political authorization mechanism, not as a general history of Roman religion. ^src-divination-republic"]
    }
  ]
```

Compile and stage the candidates:

```bash
python3 scripts/ingest_workflow.py compile-articles /home/user/Documents/rome articles.jsonl
python3 scripts/ingest_workflow.py stage /home/user/Documents/rome \
  _staging/_work/article-intents.jsonl
python3 scripts/ingest_workflow.py audit /home/user/Documents/rome
```

`article_type` routes deterministically: `entity` to `entities/`, `concept` to `concepts/`, and `scenario` to `scenarios/`. The title derives a stable lowercase slug with conjunctions such as `and` removed from filenames unless an explicit target violates the rule, in which case compilation fails. Same-target candidates must share one `focus`; conflicting focuses fail rather than producing a coupled page.

`focus` is required. It defines the article's single bounded subject and is emitted as the `scope` frontmatter field and a `## Scope` section. Use `sections` for cohesive prose organized around that subject; `claims` remains the fallback for evidence-only candidates. Do not combine adjacent topics merely because they share a source.

Each projected page must carry the matching `facets.type` value (`entity`, `concept`, or `scenario`), a summary of at most 200 characters, at most five slash-delimited tags, at least two related wikilinks, and citation markers that occur in the generated body. The compiler keeps article candidates staged, so promotion remains an explicit review decision.
For a complete candidate-block pass, use the batch projector before staging:

```bash
python3 scripts/ingest_workflow.py project-candidates /home/user/Documents/rome \
  --candidates _staging/_work/candidates
python3 scripts/ingest_workflow.py stage /home/user/Documents/rome \
  _staging/_work/projected-article-intents.jsonl
```

The projector is conservative: it extracts bounded named entities, concept candidates, and explicit case-study scenarios from the source-isolated evidence; removes cross-category filename collisions; requires a single focus per target; and preserves sampled-source boundaries. Use `stage --replace` only when regenerating artifacts owned by the same projection run.

### Create and patch intents

```json
{
  "target": "references/example.md",
  "operation": "create",
  "frontmatter": {
    "title": "Example",
    "category": "references",
    "tags": ["type/reference", "period/principate"],
    "sources": ["_raw/example.pdf"],
    "summary": "One concise sentence no longer than 200 characters.",
    "provenance": {"extracted": 0.8, "inferred": 0.1, "ambiguous": 0.1},
    "facets": {"domain": [], "type": ["reference"], "period": ["principate"], "place": [], "material": [], "subject": []}
  },
  "citations": ["^src-example"],
  "body": "# Example\n\nSource-grounded content. ^src-example"
}
```

Canonical tags are slash-delimited, contain no colons, and are limited to five entries. Complete filtering belongs in `facets`; tags are a bounded projection. Existing `relationships:` entries use only `extends`, `implements`, `contradicts`, `derived_from`, `uses`, `replaces`, `related_to`, or `part_of`.

A `patch` intent targets an existing page and is rendered as `<target>.patch.md` under `_staging/`. Promotion applies exact deletion lines, additions, and explicitly listed frontmatter fields only after the audit passes.

## Recovery

If audit fails, fix or discard the staged artifact and rerun `audit`; no live page or raw source is touched. If promotion fails partway through, the coordinator restores already-written targets from in-memory preimages. The staged artifacts remain available for inspection. A raw source is eligible for archiving only after its staged intent or explicit review decision is durable and its hash matches.
