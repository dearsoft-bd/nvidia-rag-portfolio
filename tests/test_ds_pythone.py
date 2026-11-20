import tempfile
import unittest
from pathlib import Path

from ds_pythone import AgentTools


class DSPythoneToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        docs = Path(self.temp_dir.name)
        (docs / "guide.md").write_text(
            "The safe agent searches project documents and cites evidence.",
            encoding="utf-8",
        )
        self.agent = AgentTools(docs_dir=docs)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_search_and_status_are_offline(self) -> None:
        matches = self.agent.search_docs("How does the agent cite evidence?")
        status = self.agent.status()

        self.assertTrue(matches)
        self.assertEqual(status["name"], "DS-Pythone")
        self.assertIn("search_docs", status["tools"])

    def test_read_doc_rejects_path_traversal(self) -> None:
        with self.assertRaises(ValueError):
            self.agent.read_doc("../.env")

    def test_read_doc_allows_markdown_inside_docs(self) -> None:
        content = self.agent.read_doc("guide.md")
        self.assertIn("safe agent", content)


if __name__ == "__main__":
    unittest.main()
