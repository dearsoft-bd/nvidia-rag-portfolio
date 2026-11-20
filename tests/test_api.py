import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

from rag_cli import ask_nvidia


class FakeCompletionHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0"))
        self.server.request_payload = json.loads(self.rfile.read(content_length))
        self.server.authorization = self.headers.get("Authorization")
        response = json.dumps(
            {"choices": [{"message": {"content": "Mock grounded answer [1]"}}]}
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format: str, *args: object) -> None:
        return


class ApiIntegrationTests(unittest.TestCase):
    def test_openai_compatible_request_and_response(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeCompletionHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with patch.dict(
                os.environ,
                {
                    "NVIDIA_API_KEY": "test-key",
                    "NVIDIA_MODEL": "test/model",
                    "NVIDIA_BASE_URL": f"http://127.0.0.1:{server.server_port}/v1",
                },
                clear=False,
            ):
                answer = ask_nvidia("Test grounded question")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(answer, "Mock grounded answer [1]")
        self.assertEqual(server.authorization, "Bearer test-key")
        self.assertEqual(server.request_payload["model"], "test/model")
        self.assertIn("Test grounded question", server.request_payload["messages"][0]["content"])


if __name__ == "__main__":
    unittest.main()
