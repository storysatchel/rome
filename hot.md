---
title: Hot Cache
updated: "2026-10-29T20:16:20Z"
---

# Hot Cache

*A ~500-word semantic snapshot of recent activity. Updated after every major write operation.*

## Recent Activity

- [2026-10-29T20:16:20Z] Committed 91 new focused entity, concept, and scenario articles plus 13 live-page patches. Eighty duplicate staged reference files matched existing live pages byte-for-byte and were cleared; no category page or patch remained staged. Internal `_meta/` and `_work/` control artifacts remain for audit provenance.
- [2026-10-29T19:06:35Z] Committed the audited Roman-history ingest: 80 new reference pages and 13 consolidated live-page patches are active; all 95 raw sources passed hash checks and moved to `_raw/_archived/`, with provenance recorded in `.manifest.json`.
- [2026-10-29T00:00:00Z] Reclassified all six former bibliographic blockers: direct source evidence promoted Barry, Cousins, Death and Dynasty, Divination, Empire and Memory, and the EBSCO-hosted *Birthing Romans* review to normal staged references; no review records remain.

## Active Threads

- The location hierarchy is source-grounded, not a fabricated gazetteer: every Province/Region scaffold node that no scenario ever actually used was NOT created (e.g. no "Syria," "Crete," "Cyprus" entities exist despite being real Roman provinces, because nothing in the ingested sources is set there).
- A handful of scenarios have no location at all in their cited source material (e.g. `egnatius-mecennius-wife-killing`, `jewish-merchants-stolen-goods-ruling`, `trial-of-titinia-witchcraft-accusation`) — left unlinked rather than fabricating a "Rome" guess, per the vault's no-fabrication rule.
- Location entities use a `relationships: [{target: "[[entities/<parent>]]", type: part_of}]` convention (new this round) to encode the hierarchy; scenario pages that record *where* something happened additionally got an `occurred_at` relationship pointing at the specific location entity (introduced by one batch, adopted as the convention — not yet retrofitted onto every older scenario, only ones touched this round).
- 9 archived/redirect tombstones now exist in the vault (6 from the scenario-mining pass, 3 new this round: Chalcis-dup, Arausio-dup→n/a merged in place, Janiculum Hill, Catiline's extortion trial) — all intentional, never delete, kept for link resolvability.
- The 7 "economic forces" concept pages (ager-publicus, land-and-agrarian-conflict, roman-economy-and-trade, roman-provincial-administration, elite-family-strategy, fall-of-the-roman-republic, plus their new sub-pages) now rest on full-text reads of their source books. Every *other* concept page in the vault still reflects only the original light framing-chapter pass — not yet deep-dived.
- The deep-read surfaced a real task-assumption failure worth remembering: Marin's book was assumed to detail Augustus's 27/23 BC settlement steps; a full read showed she has no Augustus chapter at all (narrative ends at Actium). The subagent reported this as a finding instead of inventing settlement content — the pattern to keep reinforcing when assigning deep-reads against an assumed-but-unverified table of contents.

## Key Takeaways

- The wiki's geography is now queryable top-down: e.g. everything under `entities/latium` → `entities/rome` → `entities/forum-romanum` traces to a specific building, and everything under `entities/numidia` traces to the Jugurthine War material.
- Concurrent-write races on heavily-shared scaffold nodes (`entities/rome`, `entities/forum-romanum`, `entities/capitoline-hill`) were largely self-healed by sibling batches re-reading and merging rather than clobbering — only 3 location entities needed manual post-hoc reconciliation.
- Two corrections from the deep-read: *tributum* was mischaracterized vault-wide as "a mandatory war-loan" (sourced from Rosenstein's framing-level mention); Pearson's dedicated chapter shows it was a tax with occasional political rebates, not a loan — corrected on `concepts/roman-provincial-administration`. Elite-family-strategy's Fabii Maximi "single 180 BC adoption" was also corrected to a double adoption (Aemilianus + Servilianus, both rescuing the line in parallel) per McCall's full text.

## Flagged Contradictions

- Mommsen (1854-56) vs. Watts (2018) on Caesar's monarchy — restorative outcome vs. tragic loss of self-rule. — `concepts/fall-of-the-roman-republic`
- Wildfang vs. DiLuzio (*A Place at the Altar*, corrupted source) on specifics of Vestal political assertiveness. — `entities/vestal-virgins`
- Marin (elite-driven concealment) vs. Watts (popular demand for autocracy) on the mechanism behind Augustus's consolidation. — `entities/augustus`
- Astin (elite occupation of public land displaced small farmers) vs. Roselaar (population growth priced farmers off *private* land) on 2nd-century agrarian distress. — `concepts/land-and-agrarian-conflict`
- Pennell (Cicero defended Catiline in his 65 BC extortion trial) vs. Alexander (Cicero only considered it; Clodius prosecuted, possibly collusively) — `scenarios/catiline-praevaricatio-acquittal-65-bc`
- Campbell (via `entities/sulla`, "as many as nine thousand" proscription deaths) vs. Marin (`concepts/precedent-escalation-in-marin`, ~40 senators + ~1,600 equestrians in the first wave) — not reconciled, different source traditions on Sulla's proscription scale.
