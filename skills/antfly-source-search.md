---
title: Antfly Source Search
category: skills
tags: [type/metadata, subject/ingest-pipeline]
summary: Commands for searching the Antfly rome corpus of ingested books by hybrid, exact, filtered and HyDE queries.
lifecycle: draft
---

# Antfly source search

The `rome` Antfly table holds ~142k chunks (about 1,200 characters each) from the books in `_raw/_archived/` and the pre-extracted `_raw/_extracted/` text. Server: `ANTFLY_URL` (default `http://127.0.0.1:18080`). Dense index `body_dense` (OpenAI `text-embedding-3-small`, 768 dimensions); the default full-text index covers the same chunks.

## 1. Vault CLI (use this one)

```bash
R="uv run --no-project --with antfly-sdk python scripts/raw_source_search.py"
$R search . "how were consuls elected" --backend antfly --limit 10
```

Results: `{source, locator, text, snippet, score, index_scores, work_id, id, previous_id, next_id, section}`. Passages that overlap one already returned from another file encoding of the same work are dropped.

| Need | Flag |
|---|---|
| Names, titles, Latin terms: keyword only | `--exact` |
| Everything except one work (e.g. a book that floods the results) | `--exclude-work <work_id>` (repeatable) |
| Only one work | `--work <work_id>` |
| Read around a hit | `$R lookup "<id>" --before 2 --after 2` |

`ANTFLY_URL`, `ANTFLY_TABLE` and `ANTFLY_INDEX` override the target. Keyword matching also tries ligature spellings (`pontiﬁcal`).

**Writing queries.** The best results combine a period name with an event or institution ("Fabius Pictor Delphi Forum Boarium"). A bare name returns noise (`Opimia` hits the Basilica Opimia and a cookbook); use `--exact` with a distinguishing second word instead. Long natural-language questions pull in off-topic keyword matches; shorten them.

## 2. Plain `antfly` CLI

```bash
export ANTFLY_URL=http://127.0.0.1:18080   # required: without it `antfly lookup` prints nothing and exits 0
antfly query --table rome --semantic-search "exile to escape prosecution" \
  --full-text-search 'body:exile' --indexes body_dense \
  --fields source_relative_path,page_numbers,body --limit 8
```

## 3. HyDE (only when plain search fails)

HyDE writes a hypothetical answer, embeds it, and searches near it. It needs `OPENAI_API_KEY` (direnv loads it) and costs a few cents per run. Smoketest result: for "why would Romans punish their priestesses after a great battle" it did worse than plain search, because the keyword half matched "battle" and "punish" in unrelated passages and the semantic half returned generic Vestal material. Lower the keyword weight for questions:

```bash
cd ~/Desktop/gavmor/antfly-hyde
DIRENV_LOG_FORMAT= direnv exec . uv run python app/hyde.py "<question>" \
  --provider openai --table rome --index body_dense --samples 2 --limit 8 \
  --lexical-weight 0.3 --brief
```

`--brief` prints one record per hit (source, pages, id, passage) instead of raw Antfly JSON. HyDE output has no `work_id` or dedupe; run the vault CLI with the names it surfaces. The hypothetical passage is only a search aid.

## Not working

`antfly agents retrieval --generate` and the REST `steps.generation` return `400 invalid retrieval agent request` with an OpenAI generator. There is no supported generated-answer path; summarise the passages yourself and cite them.
