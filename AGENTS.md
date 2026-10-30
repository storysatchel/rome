# Rome vault: agent rules

This is an Obsidian wiki on the Roman world, built from the books in `_raw/`. Page contracts and the staging/audit workflow are in `skills/ingestion-workflow-operations.md`.

## Researching sources

Before writing or enriching a page, search the source corpus. Full syntax is in `skills/antfly-source-search.md`; in short:

```bash
uv run --no-project --with antfly-sdk python scripts/raw_source_search.py search . "<question>" --backend antfly --limit 10
uv run --no-project --with antfly-sdk python scripts/raw_source_search.py lookup "<chunk id>"   # a hit plus its neighbours
```

The corpus is a local Antfly server (`rome` table, hybrid semantic + keyword search). If it is unreachable the command fails; do not substitute guesses. `--backend sqlite` is the lexical fallback and needs `raw_source_search.py index` first. Use these scripts, not the bare `antfly` CLI: the scripts default `ANTFLY_URL`, while `antfly lookup` with the variable unset prints nothing and exits 0.

## Hits are leads, not evidence

1. A hit is a passage found by similarity. It can miss the qualifier, negation or speaker in the neighbouring text. Read the chunk before and after (`lookup`) before using it.
2. Resolve who or what every assertion is about. A hit about another person is not evidence about the page subject.
3. Search for the subject across the whole corpus, not just the books already cited on the page. A claim you cannot find in any source is not made: the absence of support is a finding, not a gap to fill from memory.
4. Do not use `antfly agents retrieval --generate` or any generated answer as a source. Generated text, including HyDE hypothetical passages, is never evidence.

## Recording research

After enriching a page, append one line to `log.md`, in its existing style:

```
- [2026-10-30T12:00:00Z] RESEARCH page="entities/x" queries=9 works=wildfang-rome-s-vestal-virgins,... ranges="Wildfang PDF pp.95-96 (printed 80-81)" limits="no translation of Livy 22 in corpus"
```

`ranges` are the pages or chunks you actually read, and `limits` are what the corpus could not tell you. Nothing validates this line mechanically; it is how a reviewer checks the research.

## Corroboration and citation

- Count independent **works**, not files. Every hit carries `work_id`; the same book exists as PDF, EPUB and extracted `.txt`, and those are one source. Two modern translations or editions of one ancient text are one ancient witness. `scripts/work_ids.json` maps file stems to a shared `work_id`; add an entry when you find a split pair.
- **`p.N` is the PDF file's page, not the printed page.** They differ (offsets of +15 and +20 were seen). The vault cites printed pages: read the running header or page-number line in the passage and its neighbours, and cite as `p.N.1–p.M.1, printed pp.X–Y`. If you cannot establish the printed page, say `PDF p.N` and nothing else.
- EPUB and text hits have no pages; their locator is `chunk.N`, which only re-finds the passage inside Antfly. For text files, look for printed headers in the chunk text (e.g. `Page 149`). Paths are rooted at `_raw/` (`_raw/X`, `_raw/_extracted/X`).

## Known limits of the corpus

- *A Place at the Altar* (corrupt PDF) is not indexed. Only chapters 6–7 are known from an earlier manual read. There is no Livy translation or Plutarch in the corpus, so ancient testimony arrives only through modern books.
- PDF text has defects: missing spaces, `(cid:NN)` and private-use glyphs, broken accents, ligatures (`ﬁ`, `ﬂ`), footnote numbers glued to words, and text-file chunks split by printer slug lines. Search expands ligature spellings automatically; for other damage try variant wordings. If a prominent book returns nothing, suspect extraction quality before concluding it is silent.
- EPUBs without a table of contents have no chapter breadcrumbs.
- Combined scores are all small (about 0.015–0.032) and do not separate strong hits from weak ones. Judge relevance by reading, and use `index_scores` (`full_text`, `body_dense`) to see which half matched.
