import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.antfly_search import hits_to_results, search_antfly, source_paths_by_work

PASSAGE = ("The Vestal Opimia was convicted of incestum after Cannae and the college of pontiffs "
           "ordered the sentence carried out beneath the earth near the Colline Gate")


def hit(relative, body, pages=None, hid="h"):
    props = {"source_relative_path": relative, "body": body, "page_numbers": pages}
    return SimpleNamespace(field_id=hid, field_score=1.0,
                           field_source=SimpleNamespace(additional_properties=props))


class PrintedPageTests(unittest.TestCase):
    def test_locator_carries_printed_page_when_it_differs(self):
        labels = {("_archived/a.pdf", 95): "80", ("_archived/a.pdf", 96): "81"}
        printed = lambda relative, page: labels.get((relative, page))
        single, spanning = hits_to_results([hit("_archived/a.pdf", "x", [95])], printed=printed)[0], \
            hits_to_results([hit("_archived/a.pdf", "y", [95, 96])], printed=printed)[0]
        self.assertEqual(single["locator"], "p.95 (printed 80)")
        self.assertEqual(spanning["printed_pages"], "80-81")

    def test_no_printed_page_means_plain_pdf_locator(self):
        result = hits_to_results([hit("_archived/a.pdf", "x", [95])], printed=lambda *_: None)[0]
        self.assertEqual(result["locator"], "p.95")
        self.assertIsNone(result["printed_pages"])


class PaginatedCopyPreferredTests(unittest.TestCase):
    def test_pdf_copy_replaces_a_pageless_text_copy_of_the_same_passage(self):
        shifted = "Cannae and the college of pontiffs ordered the sentence carried out beneath the earth near the Colline Gate and more"
        hits = [hit("_extracted/Livia.txt", shifted, None, hid="txt"), hit("_archived/Livia.pdf", PASSAGE, [4], hid="pdf")]
        results = hits_to_results(hits)
        self.assertEqual([r["id"] for r in results], ["pdf"])
        self.assertEqual(results[0]["locator"], "p.4")


class WorkFilterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        raw = Path(self.temp.name)
        for directory, name in (("_archived", "Livia.pdf"), ("_extracted", "Livia.txt"), ("_archived", "Domina.pdf")):
            (raw / directory).mkdir(exist_ok=True)
            (raw / directory / name).write_text("x")
        self.raw = raw
        self.calls = []
        outer = self

        class Client:
            def query(self, table, **arguments):
                outer.calls.append(arguments)
                return SimpleNamespace(responses=[SimpleNamespace(hits=SimpleNamespace(hits=[]))])
        self.client = Client()

    def tearDown(self):
        self.temp.cleanup()

    def test_paths_are_grouped_by_work(self):
        paths = source_paths_by_work(self.raw, {})
        self.assertEqual(sorted(paths["livia"]), ["_archived/Livia.pdf", "_extracted/Livia.txt"])

    def test_work_filter_is_sent_to_the_server(self):
        search_antfly("Vestal", client=self.client, works=["livia"], keyword_only=True, raw_root=self.raw)
        sent = self.calls[0]["filter_query"]["bool"]["should"]
        self.assertEqual({clause["term"]["value"] for clause in sent}, {"_archived/Livia.pdf", "_extracted/Livia.txt"})
        self.assertNotIn("semantic_search", self.calls[0])

    def test_excluded_work_goes_in_the_exclusion_query(self):
        search_antfly("Vestal", client=self.client, exclude_works=["domina"], raw_root=self.raw)
        sent = self.calls[0]["exclusion_query"]["bool"]["should"]
        self.assertEqual([clause["term"]["value"] for clause in sent], ["_archived/Domina.pdf"])

    def test_unknown_work_id_is_an_error_not_an_empty_result(self):
        with self.assertRaisesRegex(ValueError, "unknown work_id"):
            search_antfly("Vestal", client=self.client, works=["nonsense"], raw_root=self.raw)


if __name__ == "__main__":
    unittest.main()
