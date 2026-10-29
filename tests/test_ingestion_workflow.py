from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.entity_resolution_engine import CanonicalEntityResolver, ExistingEntity, Mention
from scripts.ingest_workflow import (
    apply_patch,
    archive_processed_sources,
    audit_staged,
    compile_article_intents,
    slugify_title,
    inventory_sources,
    prepare_processed_manifest,
    promote,
    stage_page_intents,
    write_jsonl,
)


class ResolverTests(unittest.TestCase):
    def test_exact_name_and_alias_merge_but_context_conflict_is_held(self) -> None:
        mentions = [
            Mention("a", "Agrippa", "one", entity_type="person", period=("principate",), place=("rome",)),
            Mention("b", "Marcus Vipsanius Agrippa", "two", entity_type="person", aliases=("Agrippa",), period=("principate",), place=("rome",)),
            Mention("c", "Agrippa", "three", entity_type="place", period=("republic",), place=("sicily",)),
        ]
        result = CanonicalEntityResolver([
            ExistingEntity("entities/marcus-vipsanius-agrippa.md", "Marcus Vipsanius Agrippa", ("Agrippa",), "person", ("principate",), ("rome",))
        ]).resolve(mentions)
        self.assertEqual(set(result.clusters), {"entities/marcus-vipsanius-agrippa.md", "candidate:agrippa"})
        self.assertEqual(len(result.clusters["entities/marcus-vipsanius-agrippa.md"]), 2)
        self.assertEqual(len(result.held), 1)

    def test_resolution_is_order_independent(self) -> None:
        raw = [
            {"name": "Thermae Agrippae", "source_id": "b", "entity_type": "building", "aliases": ["Baths of Agrippa"], "place": ["rome"]},
            {"name": "Baths of Agrippa", "source_id": "a", "entity_type": "building", "place": ["rome"]},
        ]
        first = CanonicalEntityResolver().resolve(raw).as_dict()
        second = CanonicalEntityResolver().resolve(reversed(raw)).as_dict()
        self.assertEqual(first, second)

    def test_worker_sharding_is_stable(self) -> None:
        mention = Mention("m", "Aqua Virgo", "source", tags=("theme/infrastructure/water",))
        left = CanonicalEntityResolver.worker_for_block("facet:theme/infrastructure/water", 7)
        right = CanonicalEntityResolver.worker_for_block("facet:theme/infrastructure/water", 7)
        self.assertEqual(left, right)
        self.assertTrue(CanonicalEntityResolver.blocking_keys(mention))


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.vault = Path(self.tempdir.name)
        (self.vault / "_raw").mkdir()
        (self.vault / "references").mkdir()
        (self.vault / "_staging").mkdir()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_inventory_is_sorted_and_hashed(self) -> None:
        (self.vault / "_raw" / "b.pdf").write_bytes(b"b")
        (self.vault / "_raw" / "a.pdf").write_bytes(b"a")
        records = inventory_sources(self.vault)
        self.assertEqual([record.source_rel for record in records], ["_raw/a.pdf", "_raw/b.pdf"])
        self.assertEqual([record.block for record in records], ["B00", "B00"])
        self.assertEqual(records[0].content_hash.startswith("sha256:"), True)

    def test_stage_audit_promote_and_archive_are_safe(self) -> None:
        raw = self.vault / "_raw" / "source.pdf"
        raw.write_bytes(b"source")
        intent_file = self.vault / "intents.jsonl"
        write_jsonl(intent_file, [{
            "target": "references/source.md",
            "operation": "create",
            "frontmatter": {
                "title": "Source",
                "category": "references",
                "tags": ["type/reference"],
                "sources": ["_raw/source.pdf"],
                "summary": "A staged source page.",
                "provenance": {"extracted": 1.0, "inferred": 0.0, "ambiguous": 0.0},
                "facets": {"domain": [], "type": ["reference"], "period": [], "place": [], "material": [], "subject": []},
            },
            "citations": ["^src-test"],
            "body": "# Source\n\n[[entities/rome]] and [[entities/augustus]]. ^src-test",
        }])
        outputs = stage_page_intents(self.vault, intent_file)
        self.assertEqual(outputs, ["_staging/references/source.md"])
        self.assertEqual(audit_staged(self.vault)["ok"], True)
        with self.assertRaises(ValueError):
            promote(self.vault, confirm=False)
        inventory_path = self.vault / "_staging" / "_work" / "inventory.jsonl"
        write_jsonl(inventory_path, (record.as_dict() for record in inventory_sources(self.vault)))
        prepared = prepare_processed_manifest(self.vault)
        self.assertEqual(prepared, ["_raw/source.pdf"])
        result = promote(self.vault, confirm=True, archive_raw=True)
        self.assertIn("references/source.md", result["files"])
        self.assertTrue((self.vault / "references/source.md").exists())
        self.assertTrue((self.vault / "_raw/_archived/source.pdf").exists())
        self.assertTrue((self.vault / ".manifest.json").exists())
        manifest = json.loads((self.vault / ".manifest.json").read_text())
        self.assertEqual(manifest["stats"]["total_sources_ingested"], 1)


    def test_article_compiler_routes_merges_and_stages_typed_pages(self) -> None:
        articles = self.vault / "articles.jsonl"
        write_jsonl(articles, [
            {
                "article_type": "entity",
                "title": "Roman Senate",
                "focus": "The Senate as an emergency decision institution",
                "sources": ["B03:crisis.pdf"],
                "links": ["concepts/roman-republic", "concepts/senatus-consultum-ultimum"],
                "citations": ["^src-crisis"],
                "summary": "The Senate as a Roman institution for collective political decision-making.",
                "facets": {"domain": ["political"], "period": ["republic"], "place": ["rome"]},
                "claims": [{"text": "The Senate appears in the source as an emergency decision institution.", "citation": "^src-crisis"}],
            },
            {
                "article_type": "entity",
                "title": "Roman Senate",
                "focus": "The Senate as an emergency decision institution",
                "sources": ["B03:divination.pdf"],
                "links": ["concepts/roman-republic", "concepts/senatus-consultum-ultimum"],
                "citations": ["^src-divination"],
                "summary": "The Senate as a Roman institution for collective political decision-making.",
                "facets": {"domain": ["political"], "period": ["late-republic"], "place": ["rome"]},
                "claims": [{"text": "Religious knowledge could enter senatorial political deliberation.", "citation": "^src-divination"}],
            },
            {
                "article_type": "concept",
                "title": "Divinatory Authorization in Late Republican Rome",
                "focus": "The political authorization of signs in the late Republic",
                "sources": ["B03:divination.pdf"],
                "links": ["concepts/roman-religion-and-augury", "references/divination"],
                "citations": ["^src-divination"],
                "summary": "How divination shaped political interpretation and decision-making in Rome.",
                "facets": {"domain": ["political"], "period": ["late-republic"], "place": ["rome"]},
                "claims": [{"text": "The source connects divination with Roman political decisions.", "citation": "^src-divination"}],
            },
            {
                "article_type": "scenario",
                "title": "Catiline's Emergency Decrees (63 BC)",
                "focus": "Testing emergency decisions through the Catilinarian crisis",
                "sources": ["B03:crisis.pdf"],
                "links": ["concepts/senatus-consultum-ultimum", "concepts/fall-of-the-roman-republic"],
                "citations": ["^src-crisis"],
                "summary": "A scenario for examining emergency responses to the Catilinarian conspiracy.",
                "facets": {"domain": ["political"], "period": ["late-republic"], "place": ["rome"]},
                "claims": [{"text": "The conspiracy provides a case for studying republican crisis management.", "citation": "^src-crisis"}],
            },
        ])
        intents = compile_article_intents(self.vault, articles)
        self.assertEqual([intent["target"] for intent in intents], [
            "concepts/divinatory-authorization-in-late-republican-rome.md",
            "entities/roman-senate.md",
            "scenarios/catilines-emergency-decrees-63-bc.md",
        ])
        self.assertEqual(slugify_title("A and B"), "a-b")
        senate = next(intent for intent in intents if intent["target"] == "entities/roman-senate.md")
        self.assertEqual(senate["operation"], "create")
        self.assertEqual(senate["frontmatter"]["facets"]["type"], ["entity"])
        self.assertEqual(senate["frontmatter"]["scope"], "The Senate as an emergency decision institution")
        self.assertIn("## Scope", senate["body"])
        self.assertNotIn("-and-", senate["target"])
        intent_file = self.vault / "article-intents.jsonl"
        write_jsonl(intent_file, intents)
        staged = stage_page_intents(self.vault, intent_file)
        self.assertEqual(len(staged), 3)
        self.assertTrue(audit_staged(self.vault)["ok"])

    def test_article_compiler_rejects_conflicting_focuses(self) -> None:
        articles = self.vault / "articles.jsonl"
        write_jsonl(articles, [
            {
                "article_type": "concept",
                "title": "Focused Concept",
                "focus": "First bounded subject",
                "sources": ["source-a"],
                "citations": ["^src-a"],
                "summary": "A focused concept.",
                "links": ["concepts/a", "concepts/b"],
            },
            {
                "article_type": "concept",
                "title": "Focused Concept",
                "focus": "Different bounded subject",
                "sources": ["source-b"],
                "citations": ["^src-b"],
                "summary": "A focused concept.",
                "links": ["concepts/a", "concepts/b"],
            },
        ])
        with self.assertRaises(ValueError):
            compile_article_intents(self.vault, articles)

    def test_article_compiler_emits_patch_for_existing_target(self) -> None:
        target = self.vault / "concepts" / "existing.md"
        target.parent.mkdir()
        target.write_text("---\ntitle: Existing\n---\n\n# Existing\n", encoding="utf-8")
        articles = self.vault / "articles.jsonl"
        write_jsonl(articles, [{
            "article_type": "concept",
            "title": "Existing",
            "focus": "A bounded update to the existing concept",
            "target": "concepts/existing.md",
            "sources": ["B03:source.pdf"],
            "citations": ["^src-existing"],
            "summary": "A new evidence summary for an existing concept.",
            "claims": [{"text": "The source adds a claim.", "citation": "^src-existing"}],
        }])
        intents = compile_article_intents(self.vault, articles)
        self.assertEqual(intents[0]["operation"], "patch")
        self.assertIn("concepts/existing.md.patch.md", intents[0]["target"] + ".patch.md")
        self.assertIn("^src-existing", intents[0]["content"])
    def test_patch_application_updates_exact_lines_and_frontmatter(self) -> None:
        target = "---\ntitle: Target\nupdated: old\n---\n\n# Target\n\nold line\n\n## Sources\n\n- old\n"
        patch = "---\ntarget: concepts/target.md\noperation: patch\nupdated_fields: [updated]\nupdated: new\n---\n\n# Patch\n\n## Additions\n\n- new line\n\n## Deletions\n\n- old line\n"
        result = apply_patch(target, patch)
        self.assertIn("updated: \"new\"", result)
        self.assertIn("- new line", result)
        self.assertNotIn("old line", result)

    def test_archive_rejects_nested_or_hash_mismatched_sources(self) -> None:
        nested = self.vault / "_raw" / "nested"
        nested.mkdir()
        (nested / "source.pdf").write_bytes(b"source")
        manifest = self.vault / "_staging" / "_work" / "processed_sources.manifest"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("_raw/nested/source.pdf\n")
        with self.assertRaises(ValueError):
            archive_processed_sources(self.vault)


if __name__ == "__main__":
    unittest.main()
