"""Offline regression tests for the existing Antfly search interface.

Run: python -m unittest discover -s tests -p 'test_hybrid_search_contract.py'
No Antfly or embedding service is contacted.
"""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from scripts.antfly_search import search_antfly


class RecordingClient:
    def __init__(self, hits=()):
        self.calls = []
        self.hits = hits

    def query(self, table, **arguments):
        self.calls.append((table, arguments))
        return SimpleNamespace(responses=[SimpleNamespace(hits=SimpleNamespace(hits=self.hits))])


class HybridSearchContractTests(unittest.TestCase):
    def test_hybrid_sends_both_query_components_and_selected_index(self):
        client = RecordingClient()
        search_antfly("pontifical rites", client=client, table="test_table", index="new_index")
        table, args = client.calls[0]
        self.assertEqual(table, "test_table")
        self.assertEqual(args["semantic_search"], "pontifical rites")
        self.assertEqual(args["full_text_search"], {"match": "pontifical rites pontiﬁcal"})
        self.assertEqual(args["indexes"], ["new_index"])

    def test_index_environment_override_and_explicit_override(self):
        client = RecordingClient()
        with patch.dict(os.environ, {"ANTFLY_INDEX": "environment_index", "ANTFLY_TABLE": "environment_table"}):
            search_antfly("rites", client=client)
            search_antfly("rites", client=client, table="explicit_table", index="explicit_index")
        self.assertEqual(client.calls[0][0], "environment_table")
        self.assertEqual(client.calls[0][1]["indexes"], ["environment_index"])
        self.assertEqual(client.calls[1][0], "explicit_table")
        self.assertEqual(client.calls[1][1]["indexes"], ["explicit_index"])

    def test_keyword_only_does_not_send_semantic_index(self):
        client = RecordingClient()
        search_antfly("rites", client=client, index="unused", keyword_only=True)
        args = client.calls[0][1]
        self.assertEqual(args["full_text_search"], {"match": "rites"})
        self.assertNotIn("semantic_search", args)
        self.assertNotIn("indexes", args)

    def test_separate_component_scores_survive_result_mapping(self):
        hit = SimpleNamespace(field_id="chunk", field_score=0.7,
            field_source=SimpleNamespace(additional_properties={"source_relative_path": "_archived/a.pdf", "body": "rites"}),
            field_index_scores=SimpleNamespace(additional_properties={"full_text": 0.2, "new_index": 0.5}))
        result = search_antfly("rites", client=RecordingClient([hit]), index="new_index")
        self.assertEqual(result[0]["index_scores"], {"full_text": 0.2, "new_index": 0.5})

    def test_blank_query_never_reaches_service(self):
        client = RecordingClient()
        with self.assertRaises(ValueError):
            search_antfly("  ", client=client)
        self.assertEqual(client.calls, [])


if __name__ == "__main__":
    unittest.main()
