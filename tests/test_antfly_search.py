import unittest
from types import SimpleNamespace

from scripts.antfly_search import hits_to_results, keyword_query, locator, logical_source, lookup_chunks, work_id


def hit(relative, body, pages=None, score=1.0, hid="h"):
    props = {"source_relative_path": relative, "body": body, "page_numbers": pages}
    return SimpleNamespace(field_id=hid, field_score=score,
                           field_source=SimpleNamespace(additional_properties=props))


PASSAGE = ("The Vestal Opimia was convicted of incestum after Cannae and the college of pontiffs "
           "ordered the sentence carried out beneath the earth near the Colline Gate")


class WorkIdentityTests(unittest.TestCase):
    def test_file_encodings_of_one_book_share_a_work_id(self):
        ids = {work_id(name) for name in (
            "_archived/Liviaepub.pdf", "_archived/Liviaepub.decrypted.epub", "_archived/Livia (2).epub")}
        self.assertEqual(ids, {"livia"})

    def test_curated_override_collapses_translations(self):
        overrides = {"loeb-cicero-de-re-publica": "cicero-de-re-publica",
                     "penguin-cicero-republic": "cicero-de-re-publica"}
        self.assertEqual(work_id("_archived/Loeb Cicero De Re Publica.pdf", overrides),
                         work_id("_archived/Penguin Cicero Republic.epub", overrides))

    def test_distinct_books_stay_distinct(self):
        self.assertNotEqual(work_id("_archived/Watts - Mortal Republic.pdf"),
                            work_id("_archived/Marin - Blood in the Forum.pdf"))


class ResultMappingTests(unittest.TestCase):
    def test_locators_and_logical_paths_follow_vault_conventions(self):
        self.assertEqual(locator({"page_numbers": [17]}), "p.17")
        self.assertEqual(locator({"page_numbers": [17, 18]}), "p.17-18")
        self.assertEqual(locator({"page_numbers": None, "chunk_index": 3}), "chunk.3")
        self.assertEqual(logical_source("_archived/x.pdf"), "_raw/x.pdf")
        self.assertEqual(logical_source("_extracted/x.txt"), "_raw/_extracted/x.txt")

    def test_overlapping_passage_from_another_encoding_is_returned_once(self):
        # The text file's chunk starts mid-sentence, so a prefix comparison would miss
        # the duplicate; word overlap must not.
        shifted = "Cannae and the college of pontiffs ordered the sentence carried out beneath the earth near the Colline Gate and more"
        hits = [hit("_archived/Livia.pdf", PASSAGE, [4], hid="a"),
                hit("_extracted/Livia.txt", shifted, None, hid="b"),
                hit("_archived/Livia.pdf", "An unrelated passage about grain distribution under Augustus and Tiberius.", [9], hid="c")]
        results = hits_to_results(hits, limit=10)
        self.assertEqual([r["id"] for r in results], ["a", "c"])

    def test_same_text_in_different_works_is_kept(self):
        hits = [hit("_archived/Livia.pdf", PASSAGE, [4], hid="a"), hit("_archived/Domina.pdf", PASSAGE, [8], hid="b")]
        self.assertEqual([r["id"] for r in hits_to_results(hits)], ["a", "b"])

    def test_source_and_work_filters(self):
        hits = [hit("_archived/a.pdf", "one"), hit("_archived/b.pdf", "two")]
        self.assertEqual([r["source"] for r in hits_to_results(hits, sources=["_raw/b.pdf"])], ["_raw/b.pdf"])
        self.assertEqual([r["work_id"] for r in hits_to_results(hits, exclude_works=["a"])], ["b"])
        self.assertEqual([r["work_id"] for r in hits_to_results(hits, works=["a"])], ["a"])


class LookupTests(unittest.TestCase):
    def test_returns_chunk_with_neighbours_in_reading_order(self):
        store = {
            "c1": {"body": "first", "source_relative_path": "_archived/a.pdf", "next_id": "c2"},
            "c2": {"body": "second", "source_relative_path": "_archived/a.pdf", "previous_id": "c1", "next_id": "c3"},
            "c3": {"body": "third", "source_relative_path": "_archived/a.pdf", "previous_id": "c2"},
        }
        client = SimpleNamespace(get=lambda table, key, fields=None: store[key])
        chain = lookup_chunks("c2", before=1, after=1, client=client)
        self.assertEqual([c["id"] for c in chain], ["c1", "c2", "c3"])
        self.assertEqual(lookup_chunks("c1", before=2, after=0, client=client)[0]["id"], "c1")


class KeywordQueryTests(unittest.TestCase):
    def test_adds_ligature_spelling_for_words_pdf_extraction_may_have_ligated(self):
        self.assertEqual(keyword_query("pontifical flogged"), "pontifical flogged ponti\ufb01cal \ufb02ogged")
        self.assertEqual(keyword_query("office"), "office o\ufb03ce")

    def test_words_without_ligature_letters_are_unchanged(self):
        self.assertEqual(keyword_query("Vestal Virgins"), "Vestal Virgins")


if __name__ == "__main__":
    unittest.main()
