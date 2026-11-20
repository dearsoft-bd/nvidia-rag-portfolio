import json
import threading
import unittest
import urllib.request
from urllib.parse import urlencode

from webapp import create_server


class WebAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server("127.0.0.1", 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_home_page_and_metrics(self) -> None:
        with urllib.request.urlopen(f"{self.base_url}/", timeout=3) as response:
            html = response.read().decode("utf-8")
        with urllib.request.urlopen(f"{self.base_url}/api/metrics", timeout=3) as response:
            metrics = json.load(response)

        self.assertIn("RAG Lab", html)
        self.assertEqual(metrics["cases"], 5)
        self.assertEqual(metrics["hit_rate_at_k"], 1.0)

    def test_search_returns_sources(self) -> None:
        query = urlencode({"q": "How does the project reduce unsupported answers?"})
        with urllib.request.urlopen(f"{self.base_url}/api/search?{query}", timeout=3) as response:
            payload = json.load(response)

        self.assertTrue(payload["sources"])
        self.assertTrue(payload["sources"][0]["source"].startswith("docs/welcome.md"))


if __name__ == "__main__":
    unittest.main()
