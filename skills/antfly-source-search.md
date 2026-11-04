---
title: Antfly Source Search
category: skills
tags: [type/metadata, subject/ingest-pipeline]
summary: Commands for searching the Antfly rome corpus of ingested books by hybrid, exact, filtered and HyDE queries.
lifecycle: draft
---

# Antfly source search

The `rome` Antfly table holds 141,772 chunks (`chunk_by_title`, max 1,200 characters, 180 overlap) from the books in `_raw/_archived/` and the pre-extracted `_raw/_extracted/` text. Server: `ANTFLY_URL` (default `http://127.0.0.1:18080`). Dense index `body_dense_octen`: local Ollama `hf.co/tex8/Octen-Embedding-8B-GGUF:Q4_K_M`, 4096 dimensions, cosine; documents are embedded as `passage: <text>` by the index template. The vault CLI adds Octen's `query: ` prefix. The default full-text index `full_text_index_v0` covers the same chunks. Exploratory chunk-size benchmarks are in `~/code/antfly-ollama-benchmarks/bench/`; their relevance pools and analytic spans were derived from the 1,200-character fixture, so results do not establish that size as universally optimal.

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
antfly query --table rome --semantic-search "query: exile to escape prosecution" \
  --full-text-search 'body:exile' --indexes body_dense_octen \
  --fields source_relative_path,page_numbers,body --limit 8
```

The installed CLI at `~/.local/bin/antfly` is the executable from the matching `main-7cf3812a` server image; its version string reports `dev`. For a readable index table use `antfly --no-agent index list --table rome`; for machine-readable data use `antfly --output json index list --table rome`. Global options precede the command. The previous executable is retained as `~/.local/bin/antfly-0.2.5-backup`.

### Deployment and rollback

The Docker container `antfly` runs locally built `antfly-rome:main-7cf3812a`, based on upstream commit `7cf3812a345c2f483cc0042bdb790ead6b43ce1c`. The isolated build adjusted compiler memory reservations and limited build parallelism; it did not change server behavior. Port 8080 is published only at `127.0.0.1:18080`. The image's `localhost` health check resolves to IPv6 here, but the health server listens on IPv4; the container overrides it with `wget -qO- http://127.0.0.1:4200/readyz`.

The active Docker volume is `antfly_rome_main_7cf3812a`. The stopped `antfly-pre-7cf3812a` container and its original `antfly_rome_data` volume are the pre-upgrade rollback point; `antfly_rome_backup_pre_7cf3812a` is an additional earlier copy. Upgrading changed the storage format: the old image cannot safely open the upgraded volume. Rolling back to the original volume also loses any writes made after cutover; preserve or migrate those writes first.

At cutover both indexes reported ready and 141,772 records; the dense index reported 141,772 covered/searchable and zero failed. Its native storage phase initially reported `native_building` despite being queryable.

## 3. HyDE (currently unavailable)

HyDE (`~/Desktop/gavmor/antfly-hyde/app/hyde.py`) writes a hypothetical answer, embeds it, and searches near it. Its query-time embedding must reproduce the index's document recipe. The documented OpenAI `text-embedding-3-small` (768-d) setup targeted the dropped `body_dense` index and cannot query `body_dense_octen`. The local route (`--generate-url`/`--embed-url` pointed at Ollama `/v1`, `--embed-model` Octen) is also not yet compatible: `hyde.py` embeds the generated passage without the `passage: ` prefix the index uses. Until that is added and tested, use the vault CLI. In an earlier smoketest HyDE did worse than plain search on a question because its keyword half matched generic words; it is a search aid at best, and the hypothetical passage is never evidence.

## 4. Antfly Native Agents with Local Ollama

Antfly agents can run against local Ollama models (`http://172.17.0.1:11434` from inside Docker). **Crucial configuration requirements:**
1. The Ollama URL **must include `/v1`** (Antfly appends `/chat/completions`).
2. **Always specify `"max_tokens": 4096`**. Antfly's stock default is 256 tokens; reasoning/thinking models (Nemotron, Qwen 3.8) spend all 256 tokens on their internal reasoning trace, returning empty content. With 4096 tokens, reasoning models finish thinking and emit full answers.
3. **Do not disable thinking** (`reasoning_effort: "none"`) on reasoning models; they rely on the thinking trace for table schema introspection and multi-turn query planning.

```json
"generator": {
  "provider": "ollama",
  "model": "bakeoff-qwen3-coder-q5kxl:latest",
  "url": "http://172.17.0.1:11434/v1",
  "max_tokens": 4096
}
```
*(For reasoning-augmented generation, substitute `"model": "hf.co/bartowski/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF:Q4_K_S"` with `"max_tokens": 4096`.)*
### Retrieval Agent (`antfly agents retrieval`)

1. **Pipeline Mode with Answer Generation:**
   ```bash
   antfly agents retrieval --table rome \
     --semantic-search "query: who were the Garamantes" \
     --indexes body_dense_octen \
    --generator '{"provider":"ollama","model":"bakeoff-qwen3-coder-q5kxl:latest","url":"http://172.17.0.1:11434/v1","max_tokens":4096}' \
     --limit 3 --generate
   ```
   Streams the retrieved hits and synthesized answer with citations.

2. **Agentic Tool-Calling Mode (`--intent`):**
   For conversational intent where the agent must plan queries via `build_query` and execute searches autonomously, use the deterministic champion model `bakeoff-qwen3-coder-q5kxl:latest`:
   ```bash
   antfly agents retrieval --table rome \
     --intent "Find who served as consuls in 63 BC" \
     --indexes body_dense_octen \
     --generator '{"provider":"ollama","model":"bakeoff-qwen3-coder-q5kxl:latest","url":"http://172.17.0.1:11434/v1","max_tokens":4096}' \
     --limit 3 --generate --no-streaming
   ```

### Query Builder Agent (`antfly agents query-builder`)

Translates natural language intent into structured Antfly queries (`full_text_search` or `semantic_search` targeting `body_dense_octen`):
```bash
antfly agents query-builder --intent "find consuls who were elected in 63 BC" \
  --table rome \
  --generator '{"provider":"ollama","model":"bakeoff-qwen3-coder-q5kxl:latest","url":"http://172.17.0.1:11434/v1","max_tokens":4096}'
```

**Query prefix.** Antfly embeds `semantic_search` text as given, so queries that agents or the query builder generate go out without Octen's `query: ` prefix. That costs nothing measurable: on the bench fixture, unprefixed queries against the `passage:`-prefixed index scored MRR@10 0.9635 vs 0.9583 with the prefix (n=32, within noise). The document-side `passage: ` prefix is what matters: with no prefixes at all the same fixture scores 0.9271.

### Research Agent Status
The deployed main build exposes `/db/v1/agents/research`. A non-streaming smoke request with the Qwen3-Coder generator and the `rome` table completed and returned a cited report; this is not validation of every generated claim or citation.

### Protocol Rule
Per `AGENTS.md` Rule 4, generated text is a research aid and is **never evidence** in wiki pages; always verify claims against the underlying chunk text and cited printed pages.
