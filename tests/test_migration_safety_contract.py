"""Offline migration safety contracts.

Run: python -m unittest discover -s tests -p 'test_*contract.py'
Expected failures document cutover defects; no shared services are contacted.
"""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from scripts import embedding_migration as migration


class MigrationSafetyContractTests(unittest.TestCase):
    def test_create_index_uses_separate_ollama_index_without_dropping_old(self):
        with patch.object(migration, 'index_exists', return_value=False), \
             patch.object(migration, '_antfly', return_value=SimpleNamespace(returncode=0)) as call:
            self.assertEqual(migration.cmd_create_index(None), 0)
        args = call.call_args.args
        self.assertEqual(args[:2], ('index', 'create'))
        self.assertEqual(args[args.index('--index') + 1], migration.NEW_INDEX)
        self.assertNotEqual(migration.NEW_INDEX, migration.OLD_INDEX)
        self.assertEqual(json.loads(args[args.index('--embedder') + 1]), {
            'provider': 'ollama', 'model': migration.EMBEDDER_MODEL,
            'url': migration.OLLAMA_URL_FROM_CONTAINER,
        })
        self.assertEqual(call.call_count, 1)

    def test_existing_new_index_is_not_recreated(self):
        with patch.object(migration, 'index_exists', return_value=True), \
             patch.object(migration, '_antfly') as call:
            self.assertEqual(migration.cmd_create_index(None), 0)
            call.assert_not_called()

    def test_incomplete_or_unhealthy_coverage_blocks_normal_cutover(self):
        for complete, healthy in ((False, True), (True, False), (False, False)):
            with self.subTest(complete=complete, healthy=healthy), \
                 patch.object(migration, 'index_exists', return_value=True), \
                 patch.object(migration, 'get_coverage', return_value={
                     'total': 10, 'covered': 9, 'pending': 1, 'failed': 0,
                     'complete': complete, 'healthy': healthy,
                 }), patch.object(migration, '_set_env_index') as write:
                self.assertEqual(migration.cmd_cutover(SimpleNamespace(force=False)), 1)
                write.assert_not_called()

    @unittest.expectedFailure
    def test_inconsistent_complete_flag_cannot_bypass_coverage_check(self):
        with patch.object(migration, 'index_exists', return_value=True), \
             patch.object(migration, 'get_coverage', return_value={
                 'total': 10, 'covered': 9, 'pending': 1, 'failed': 0,
                 'complete': True, 'healthy': True,
             }), patch.object(migration, '_set_env_index') as write:
            self.assertEqual(migration.cmd_cutover(SimpleNamespace(force=False)), 1)
            write.assert_not_called()

    @unittest.expectedFailure
    def test_force_cannot_bypass_incomplete_backfill(self):
        with patch.object(migration, 'index_exists', return_value=True), \
             patch.object(migration, 'get_coverage', return_value={
                 'total': 10, 'covered': 9, 'pending': 1, 'failed': 0,
                 'complete': False, 'healthy': False,
             }), patch.object(migration, '_set_env_index') as write:
            self.assertEqual(migration.cmd_cutover(SimpleNamespace(force=True)), 1)
            write.assert_not_called()

    def test_rollback_does_not_write_if_old_index_is_missing(self):
        with patch.object(migration, 'index_exists', return_value=False), \
             patch.object(migration, '_set_env_index') as write:
            self.assertEqual(migration.cmd_rollback(None), 1)
            write.assert_not_called()


if __name__ == '__main__':
    unittest.main()
