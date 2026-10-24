---
title: Hot Cache
updated: "2026-10-24T20:50:00Z"
---

# Hot Cache

*A ~500-word semantic snapshot of recent activity. Updated after every major write operation.*

## Recent Activity

- [2026-10-24T20:50:00Z] Ingested 5 new `_raw/` sources — Hudson (vehicle rhetoric in Latin literature), Bang (Roman Bazaar economic comparative history), Scarre (Penguin atlas, scanned/vision-read), Goodman (provincial urbanism periphery), Casson (travel/roads). Created 5 `references/` pages + 2 new concepts (`roman-economy-and-trade`, `roman-travel-and-transportation`); updated `roman-urban-geography`, `provinces-of-the-roman-empire`, `entities/cato-the-elder`, `entities/gaius-gracchus` (new Hudson anecdotes: Gracchus's litter-beating story, Seneca's Cato-vs-trossulus passage). Converted a Kindle `.azw3` via `ebook-convert` and vision-read a 73-page scanned atlas.
- [2026-10-24T19:15:00Z] Corrected a misdiagnosis: Roselaar's `.rar` wasn't corrupted — `bsdtar` succeeded where `unar`/`7z` failed on its RAR5 method. Ingested it: `references/roselaar-public-land-roman-republic`, updated 2 concept pages.
- [2026-10-24T09:20:00Z] Deep-read Gargola and Marin to enrich geography coverage. Expanded `concepts/roman-urban-geography` and created `concepts/provinces-of-the-roman-empire`.

## Active Threads

- Several pages rest on thin, single-source evidence (`base_confidence: 0.57`, tier: supporting) and flag incomplete sampling of large source monographs (200-500+ page books sampled via TOC/intro/conclusion + representative chapters, not read cover-to-cover) — candidates for deeper re-ingest if more thorough coverage is wanted.
- `references/place-at-the-altar-priestesses.md` (DiLuzio) is grounded in a severely corrupted source PDF (~93% zero-byte) — only ch.6-7 and bibliography recoverable.
- `references/lucretius-on-the-nature-of-things.md` source epub is a near-empty stub (TOC headers only) — mostly inferred background, not source-grounded extraction.
- `references/scarre-penguin-atlas-ancient-rome.md` is a scanned, image-only PDF (no text layer) — only 4 of 73 spreads sampled via vision; most of its 60+ maps are unexamined.
- `references/bang-roman-bazaar.md`'s OCR text layer is visibly degraded in places (ligature garbling) — numeric/table claims were not cited for that reason.

## Key Takeaways

- Three books (Mommsen, Marin, Watts) converge on the Republic's fall as a gradual multi-generational process from the Gracchi to Augustus, but sharply disagree on whether Caesar's monarchy was a tragic loss of self-government or a necessary, even benevolent, restorative outcome.
- Cicero's own career is a documented methodological fault line in the oratory corpus: Morstein-Marx and van der Blom/Gray/Steel necessarily build on his (best-surviving) speeches, while van der Blom's solo monograph argues his career was exceptional, not representative.
- The wiki now has a documented "ancient economy debate" thread: Goodman's political-vs-economic city debate and Bang's primitivist-vs-modernist trade debate are structurally the same disagreement playing out in two different scholarly literatures (urbanism and economic history).

## Flagged Contradictions

- Mommsen (1854-56) vs. Watts (2018) on Caesar's monarchy — restorative outcome vs. tragic loss of self-rule. — `concepts/fall-of-the-roman-republic`
- Wildfang vs. DiLuzio (*A Place at the Altar*, corrupted source) on specifics of Vestal political assertiveness. — `entities/vestal-virgins`
- Marin (elite-driven concealment) vs. Watts (popular demand for autocracy) on the mechanism behind Augustus's consolidation. — `entities/augustus`
- Astin (elite occupation of public land displaced small farmers) vs. Roselaar (population growth priced farmers off *private* land) on 2nd-century agrarian distress. — `concepts/land-and-agrarian-conflict`
