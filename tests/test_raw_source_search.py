import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.raw_source_search import build_index, search


class RawSourceSearchTests(unittest.TestCase):
    def test_indexes_archived_source_and_returns_located_passage(self):
        with tempfile.TemporaryDirectory() as temp:
            vault = Path(temp)
            raw = vault / "_raw"
            archived = raw / "_archived"
            archived.mkdir(parents=True)
            source = archived / "example.txt"
            source.write_text("Roman grain distribution shaped access to food.\n\nThe annona linked provisioning to imperial politics.", encoding="utf-8")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            work = vault / "_staging" / "_work"
            work.mkdir(parents=True)
            (work / "inventory.jsonl").write_text(json.dumps({
                "source_rel": "_raw/example.txt",
                "content_hash": f"sha256:{digest}",
            }) + "\n", encoding="utf-8")
            result = build_index(vault, work / "raw.sqlite3")
            self.assertEqual(result["sources_indexed"], 1)
            matches = search(work / "raw.sqlite3", "annona imperial politics", limit=5)
            self.assertEqual(matches[0]["source"], "_raw/example.txt")
            self.assertEqual(matches[0]["locator"], "section.1")
            self.assertIn("[imperial]", matches[0]["snippet"])


if __name__ == "__main__":
    unittest.main()
