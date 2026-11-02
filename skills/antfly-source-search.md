---
title: Antfly Source Search
category: skills
tags: [type/metadata, subject/ingest-pipeline]
summary: Commands for searching the Antfly rome corpus of ingested books by hybrid, exact, filtered and HyDE queries.
lifecycle: draft
---

# Antfly source search

The `rome` Antfly table holds ~142k chunks (about 1,200 characters each) from the books in `_raw/_archived/` and the pre-extracted `_raw/_extracted/` text. Server: `ANTFLY_URL` (default `http://127.0.0.1:18080`). Dense index `body_dense_nomic` (local Ollama `nomic-embed-text-cpu`, 768 dimensions, 100% local with no API rate limits); the default full-text index `full_text_index_v0` covers the same chunks.

## 1. Vault CLI (use this one)

```bash
R="uv run --no-project --with antfly-sdk --with pypdf python scripts/raw_source_search.py"
$R search . "how were consuls elected" --backend antfly --limit 10
```

Results: `{source, locator, text, snippet, score, index_scores, work_id, id, previous_id, next_id, section}`. Passages that overlap one already returned from another file encoding of the same work are dropped.

| Need | Flag |
|---|---|
| Names, titles, Latin terms: keyword only. Not a phrase match: every word is matched separately, and `index_scores` is empty | `--exact` |
| Everything except one work (e.g. a book that floods the results) | `--exclude-work <work_id>` (repeatable) |
| Only one work (searched in full, whatever its rank across the corpus) | `--work <work_id>` (an unknown id is an error) |
| Read around a hit | `$R lookup "<id>" --before 2 --after 2` |

`ANTFLY_URL`, `ANTFLY_TABLE` and `ANTFLY_INDEX` override the target. Keyword matching also tries ligature spellings (`pontiﬁcal`).

**Writing queries.** The best results combine a period name with an event or institution ("Fabius Pictor Delphi Forum Boarium"). A bare name returns noise (`Opimia` hits the Basilica Opimia and a cookbook); use `--exact` with a distinguishing second word instead. Long natural-language questions pull in off-topic keyword matches; shorten them.

## 2. Plain `antfly` CLI

```bash
export ANTFLY_URL=http://127.0.0.1:18080   # required: without it `antfly lookup` prints nothing and exits 0
antfly query --table rome --semantic-search "exile to escape prosecution" \
  --full-text-search 'body:exile' --indexes body_dense_nomic \
  --fields source_relative_path,page_numbers,body --limit 8
```

## 3. HyDE (only when plain search fails)

HyDE writes a hypothetical answer, embeds it, and searches near it. It needs `OPENAI_API_KEY` (direnv loads it) and costs a few cents per run. Smoketest result: for "why would Romans punish their priestesses after a great battle" it did worse than plain search, because the keyword half matched "battle" and "punish" in unrelated passages and the semantic half returned generic Vestal material. Lower the keyword weight for questions:

```bash
cd ~/Desktop/gavmor/antfly-hyde
DIRENV_LOG_FORMAT= direnv exec . uv run python app/hyde.py "<question>" \
  --provider openai --table rome --index body_dense_nomic --samples 2 --limit 8 \
  --lexical-weight 0.3 --brief
```

`--brief` prints one record per hit (source, pages, id, passage) instead of raw Antfly JSON. HyDE output has no `work_id` or dedupe; run the vault CLI with the names it surfaces. The hypothetical passage is only a search aid.

## 4. Antfly Native Agents with Local Ollama

Antfly agents can run against local Ollama models (`http://172.17.0.1:11434` from inside Docker). **Crucial configuration detail:** Antfly uses the Chat Completions protocol and appends `/chat/completions`, so the Ollama URL **must include `/v1`**:

```json
"generator": {
  "provider": "ollama",
  "model": "llama3.2:1b",
  "url": "http://172.17.0.1:11434/v1"
}
```

### Retrieval Agent (`antfly agents retrieval`)

1. **Pipeline Mode with Answer Generation:**
   ```bash
   antfly agents retrieval --table rome \
     --semantic-search "who were the Garamantes" \
     --indexes body_dense_nomic \
     --generator '{"provider":"ollama","model":"llama3.2:1b","url":"http://172.17.0.1:11434/v1"}' \
     --limit 3 --generate
   ```
   Streams the retrieved hits and synthesized answer with citations.

2. **Agentic Tool-Calling Mode (`--intent`):**
   For conversational intent where the agent must plan queries via `build_query` and execute searches autonomously, use a tool-capable model such as `Qwen2.5-14B-Instruct`:
   ```bash
   antfly agents retrieval --table rome \
     --intent "Find who served as consuls in 63 BC" \
     --indexes body_dense_nomic \
     --generator '{"provider":"ollama","model":"hf.co/bartowski/Qwen2.5-14B-Instruct-GGUF:Q5_K_M","url":"http://172.17.0.1:11434/v1"}' \
     --limit 3 --generate --no-streaming
   ```

### Query Builder Agent (`antfly agents query-builder`)

Translates natural language intent into structured Antfly queries (`full_text_search` or `semantic_search` targeting `body_dense_nomic`):
```bash
antfly agents query-builder --intent "find consuls who were elected in 63 BC" \
  --table rome \
  --generator '{"provider":"ollama","model":"llama3.2:1b","url":"http://172.17.0.1:11434/v1"}'
```

### Research Agent Status
In the deployed Antfly container/CLI (v0.2.5), `agents research` is not deployed (`/agents/research` returns 405 Method Not Allowed; the feature exists only in the unreleased `deep-research` development branch).

### Protocol Rule
Per `AGENTS.md` Rule 4, generated text is a research aid and is **never evidence** in wiki pages; always verify claims against the underlying chunk text and cited printed pages.
