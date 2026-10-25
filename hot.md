---
title: Hot Cache
updated: "2026-10-25T02:20:00Z"
---

# Hot Cache

*A ~500-word semantic snapshot of recent activity. Updated after every major write operation.*

## Recent Activity

- [2026-10-25T02:20:00Z] Built a Province > Region > District > Building location hierarchy across every one of the 111 scenarios. Pre-built a 27-entity shared scaffold (Italy + 9 provinces, 10 regions, Rome + its 7 major sub-districts) to bound collision risk, then ran 9 parallel batches re-reading all scenarios for every location mentioned, no matter how minor — specific temples (Jupiter Feretrius, Concordia, Vesta's Curia Hostilia), specific streets/gates (Via Appia, Colline Gate), specific villas (Scipio's at Liternum, Axius's at Reate), even legendary/literary sites (Troy, Laurentum, Drepanum from the Aeneid). Entities grew from 226 to 333. Found and merged 3 cross-batch entity duplicates (Chalcis, Arausio, Janiculum) plus one previously-missed scenario-level duplicate: Catiline's 65 BC extortion trial, documented by both Pennell and Alexander with a genuine factual disagreement over whether Cicero defended him — merged into one page with the contradiction preserved as an Open Question rather than silently picking a winner.
- [2026-10-24T22:05:00Z] Scenario-mined all 38 sources for discrete conflicts/events/contests/conspiracies — 111 scenarios, 206 new entity stubs, 6 duplicate merges.
- [2026-10-24T19:15:00Z] Corrected a misdiagnosis: Roselaar's `.rar` wasn't corrupted — `bsdtar` succeeded where `unar`/`7z` failed on its RAR5 method.

## Active Threads

- The location hierarchy is source-grounded, not a fabricated gazetteer: every Province/Region scaffold node that no scenario ever actually used was NOT created (e.g. no "Syria," "Crete," "Cyprus" entities exist despite being real Roman provinces, because nothing in the ingested sources is set there).
- A handful of scenarios have no location at all in their cited source material (e.g. `egnatius-mecennius-wife-killing`, `jewish-merchants-stolen-goods-ruling`, `trial-of-titinia-witchcraft-accusation`) — left unlinked rather than fabricating a "Rome" guess, per the vault's no-fabrication rule.
- Location entities use a `relationships: [{target: "[[entities/<parent>]]", type: part_of}]` convention (new this round) to encode the hierarchy; scenario pages that record *where* something happened additionally got an `occurred_at` relationship pointing at the specific location entity (introduced by one batch, adopted as the convention — not yet retrofitted onto every older scenario, only ones touched this round).
- 9 archived/redirect tombstones now exist in the vault (6 from the scenario-mining pass, 3 new this round: Chalcis-dup, Arausio-dup→n/a merged in place, Janiculum Hill, Catiline's extortion trial) — all intentional, never delete, kept for link resolvability.

## Key Takeaways

- The wiki's geography is now queryable top-down: e.g. everything under `entities/latium` → `entities/rome` → `entities/forum-romanum` traces to a specific building, and everything under `entities/numidia` traces to the Jugurthine War material.
- Concurrent-write races on heavily-shared scaffold nodes (`entities/rome`, `entities/forum-romanum`, `entities/capitoline-hill`) were largely self-healed by sibling batches re-reading and merging rather than clobbering — only 3 location entities needed manual post-hoc reconciliation.

## Flagged Contradictions

- Mommsen (1854-56) vs. Watts (2018) on Caesar's monarchy — restorative outcome vs. tragic loss of self-rule. — `concepts/fall-of-the-roman-republic`
- Wildfang vs. DiLuzio (*A Place at the Altar*, corrupted source) on specifics of Vestal political assertiveness. — `entities/vestal-virgins`
- Marin (elite-driven concealment) vs. Watts (popular demand for autocracy) on the mechanism behind Augustus's consolidation. — `entities/augustus`
- Astin (elite occupation of public land displaced small farmers) vs. Roselaar (population growth priced farmers off *private* land) on 2nd-century agrarian distress. — `concepts/land-and-agrarian-conflict`
- Pennell (Cicero defended Catiline in his 65 BC extortion trial) vs. Alexander (Cicero only considered it; Clodius prosecuted, possibly collusively) — `scenarios/catiline-praevaricatio-acquittal-65-bc`
