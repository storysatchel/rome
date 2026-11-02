import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
import tempfile
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.embedding_migration import (
    get_coverage,
    current_index,
    _set_env_index,
    OLD_INDEX,
    NEW_INDEX,
    ENV_KEY,
    EMBEDDER_MODEL,
    EMBEDDING_DIM,
)


class CoverageParsingTests(unittest.TestCase):
    @patch("scripts.embedding_migration._antfly_json")
    def test_parses_complete_coverage(self, mock):
        mock.return_value = {
            "status": {
                "source_coverage": {
                    "total": 141772, "covered": 141772, "pending": 0,
                    "failed": 0, "skipped": 0, "complete": True, "healthy": True,
                }
            }
        }
        cov = get_coverage("body_dense_nomic")
        self.assertTrue(cov["complete"])
        self.assertEqual(cov["covered"], 141772)
        self.assertEqual(cov["pending"], 0)

    @patch("scripts.embedding_migration._antfly_json")
    def test_parses_incomplete_coverage(self, mock):
        mock.return_value = {
            "status": {
                "source_coverage": {
                    "total": 141772, "covered": 500, "pending": 141272,
                    "failed": 0, "skipped": 0, "complete": False, "healthy": False,
                }
            }
        }
        cov = get_coverage("body_dense_nomic")
        self.assertFalse(cov["complete"])
        self.assertEqual(cov["pending"], 141272)


class EnvFileTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.env_path = Path(self.tmpdir) / ".env"
        self.env_path.write_text(
            "# Config\nOBSIDIAN_VAULT_PATH=/home/user/Documents/rome\n"
            "QMD_WIKI_COLLECTION=rome\n"
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch("scripts.embedding_migration.VAULT_ROOT")
    def test_set_env_index_adds_entry(self, mock_root):
        mock_root.__truediv__ = lambda self, other: Path(self.tmpdir) / other if other == ".env" else NotImplemented
        mock_root.tmpdir = self.tmpdir
        # Directly test with real path
        import scripts.embedding_migration as mod
        orig = mod.VAULT_ROOT
        try:
            mod.VAULT_ROOT = Path(self.tmpdir)
            _set_env_index(NEW_INDEX)
            content = self.env_path.read_text()
            self.assertIn(f"{ENV_KEY}={NEW_INDEX}", content)
            # Original entries preserved
            self.assertIn("OBSIDIAN_VAULT_PATH=", content)
        finally:
            mod.VAULT_ROOT = orig

    @patch("scripts.embedding_migration.VAULT_ROOT")
    def test_set_env_index_replaces_existing(self, mock_root):
        self.env_path.write_text(
            f"OBSIDIAN_VAULT_PATH=/x\n{ENV_KEY}={OLD_INDEX}\nOTHER=y\n"
        )
        import scripts.embedding_migration as mod
        orig = mod.VAULT_ROOT
        try:
            mod.VAULT_ROOT = Path(self.tmpdir)
            _set_env_index(NEW_INDEX)
            content = self.env_path.read_text()
            self.assertIn(f"{ENV_KEY}={NEW_INDEX}", content)
            # body_dense is a substring of body_dense_nomic, so check line-by-line
            index_lines = [l for l in content.splitlines() if l.startswith(f"{ENV_KEY}=")]
            self.assertEqual(index_lines, [f"{ENV_KEY}={NEW_INDEX}"])
            self.assertIn("OTHER=y", content)
        finally:
            mod.VAULT_ROOT = orig

    @patch("scripts.embedding_migration.VAULT_ROOT")
    def test_rollback_restores_old_index(self, mock_root):
        self.env_path.write_text(f"{ENV_KEY}={NEW_INDEX}\n")
        import scripts.embedding_migration as mod
        orig = mod.VAULT_ROOT
        try:
            mod.VAULT_ROOT = Path(self.tmpdir)
            _set_env_index(OLD_INDEX)
            content = self.env_path.read_text()
            self.assertIn(f"{ENV_KEY}={OLD_INDEX}", content)
            self.assertNotIn(NEW_INDEX, content)
        finally:
            mod.VAULT_ROOT = orig


class ConstantsTests(unittest.TestCase):
    def test_model_name(self):
        self.assertEqual(EMBEDDER_MODEL, "nomic-embed-text-cpu")

    def test_dimension(self):
        self.assertEqual(EMBEDDING_DIM, 768)

    def test_index_names(self):
        self.assertEqual(OLD_INDEX, "body_dense")
        self.assertEqual(NEW_INDEX, "body_dense_nomic")


if __name__ == "__main__":
    unittest.main()
