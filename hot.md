---
title: Hot Cache
updated: "2026-10-24T22:05:00Z"
---

# Hot Cache

*A ~500-word semantic snapshot of recent activity. Updated after every major write operation.*

## Recent Activity

- [2026-10-24T22:05:00Z] Re-scoured all 38 previously-ingested sources for discrete conflicts/events/contests/conspiracies — athletic, legal, political, military, economic — favoring obscure/petty incidents over already-covered headline events. New `scenarios/` category: 111 articles (35 political, 35 legal, 15 military, 15 economic, 7 conspiracy, 4 athletic — including Virgil's funeral games as literal athletic contests). Entities grew from 20 to 226 (every named person/place/thing involved in a scenario got a stub). 9 parallel subagents produced ~300 new pages; found and resolved 6 genuine cross-batch duplicates (same real person independently profiled by two batches — e.g. Scipio Africanus, Saturninus, two different Titus Labienus pages) by merging content and leaving redirect stubs. Vault now 402 pages, 0 dangling links, 0 true orphans.
- [2026-10-24T19:15:00Z] Corrected a misdiagnosis: Roselaar's `.rar` wasn't corrupted — `bsdtar` succeeded where `unar`/`7z` failed on its RAR5 method.
- [2026-10-24T20:50:00Z] Ingested 5 new sources (Hudson, Bang, Scarre, Goodman, Casson) — travel, economy, provincial urbanism.

## Active Threads

- Several scenario pages rest on thin, single-sentence source citations (base_confidence as low as 0.45-0.52) — flagged in their own Open Questions rather than padded with invented detail.
- 6 duplicate entity pages were converted to `lifecycle: archived` redirect stubs rather than deleted (matching the vault's existing convention from the Sandberg duplicate-scan precedent) — they remain as dead-end tombstones pointing to the canonical merged page.
- 5 new unprocessed files are still sitting in `_raw/` from an earlier drop (Hudson, Bang, Scarre, Goodman, Casson were already processed; check `_raw/` for any further new arrivals) — none currently pending as of this update.
- The scenario-mining pass deliberately did NOT re-read every chapter of every 300+ page book — several sources (Cato/Varro's farm manual, Lucretius's near-empty stub, Goodman's academic prose) yielded few or zero scenarios and this was reported honestly rather than forced.

## Key Takeaways

- The wiki now has a genuine micro-history layer beneath its thematic concept pages: specific named trials (Causa Curiana, the Vestal incestum trials, dozens from Alexander's catalog), specific battles (Caudine Forks, Clastidium), specific scandals (Marius's gold ring, the Tolosan gold affair), and specific athletic contests (the Aeneid's funeral games).
- Several real people turn out to be documented across multiple, previously-unconnected scenarios once mined this way — e.g. Cato the Elder now connects to a 184 BC Senate purge, a water-diversion lawsuit, and a public-contracts dispute, not just his Hellenism and farming-economy material.

## Flagged Contradictions

- Mommsen (1854-56) vs. Watts (2018) on Caesar's monarchy — restorative outcome vs. tragic loss of self-rule. — `concepts/fall-of-the-roman-republic`
- Wildfang vs. DiLuzio (*A Place at the Altar*, corrupted source) on specifics of Vestal political assertiveness. — `entities/vestal-virgins`
- Marin (elite-driven concealment) vs. Watts (popular demand for autocracy) on the mechanism behind Augustus's consolidation. — `entities/augustus`
- Astin (elite occupation of public land displaced small farmers) vs. Roselaar (population growth priced farmers off *private* land) on 2nd-century agrarian distress. — `concepts/land-and-agrarian-conflict`
