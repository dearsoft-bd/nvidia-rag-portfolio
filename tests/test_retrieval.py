import tempfile
import unittest
from pathlib import Path

from rag_cli import load_chunks, retrieve


class RetrievalTests(unittest.TestCase):
    def test_retrieves_citation_safeguard(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            docs = Path(directory)
            (docs / "guide.md").write_text(
                "Retrieval supplies source context.\n\n"
                "Numbered citations help readers verify factual claims.",
                encoding="utf-8",
            )
            chunks = load_chunks(docs)
            matches = retrieve(chunks, "How can readers verify facts with citations?")

        self.assertTrue(matches)
        self.assertIn("citations", matches[0][1].text.lower())

    def test_empty_query_returns_no_matches(self) -> None:
        chunks = load_chunks(Path("docs"))
        self.assertEqual(retrieve(chunks, "   "), [])


if __name__ == "__main__":
    unittest.main()
