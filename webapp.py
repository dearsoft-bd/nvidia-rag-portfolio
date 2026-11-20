#!/usr/bin/env python3
"""Local-only web interface for the dependency-free RAG project."""

from __future__ import annotations

import argparse
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from evaluation import DEFAULT_CASES, evaluate_cases, summarize
from rag_cli import ROOT, ask_nvidia, build_prompt, load_chunks, load_dotenv, retrieve

MAX_QUESTION_LENGTH = 2_000
MAX_BODY_BYTES = 16_384
PLACEHOLDER_KEYS = {"", "nvapi-REPLACE_WITH_YOUR_KEY", "nvapi-replace-me"}


class RagHTTPServer(ThreadingHTTPServer):
    chunks: list
    ui_html: bytes


class Handler(BaseHTTPRequestHandler):
    server: RagHTTPServer

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, body: bytes) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _question_from_query(self) -> str | None:
        query = parse_qs(urlparse(self.path).query)
        question = query.get("q", [""])[0].strip()
        if not question or len(question) > MAX_QUESTION_LENGTH:
            return None
        return question

    def _matches_payload(self, question: str, top_k: int = 4) -> list[dict]:
        matches = retrieve(self.server.chunks, question, top_k)
        return [
            {
                "rank": index,
                "score": round(score, 4),
                "source": chunk.source,
                "text": " ".join(chunk.text.split()),
            }
            for index, (score, chunk) in enumerate(matches, start=1)
        ]

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._send_html(self.server.ui_html)
            return
        if path == "/api/metrics":
            results = evaluate_cases(self.server.chunks, DEFAULT_CASES, top_k=3)
            self._send_json(summarize(results))
            return
        if path == "/api/search":
            question = self._question_from_query()
            if question is None:
                self._send_json(
                    {"error": "Provide a question under 2000 characters."},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            matches = self._matches_payload(question)
            self._send_json({"question": question, "sources": matches})
            return
        self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/ask":
            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > MAX_BODY_BYTES:
                raise ValueError("Invalid request size")
            payload = json.loads(self.rfile.read(content_length))
            question = str(payload.get("question", "")).strip()
            if not question or len(question) > MAX_QUESTION_LENGTH:
                raise ValueError("Provide a question under 2000 characters")
        except (ValueError, json.JSONDecodeError):
            self._send_json(
                {"error": "Provide a valid JSON question under 2000 characters."},
                HTTPStatus.BAD_REQUEST,
            )
            return

        matches = retrieve(self.server.chunks, question, 4)
        if not matches:
            self._send_json({"error": "No relevant passages found."}, HTTPStatus.NOT_FOUND)
            return

        if os.getenv("NVIDIA_API_KEY", "") in PLACEHOLDER_KEYS:
            self._send_json(
                {
                    "error": "NVIDIA API key is not configured. Retrieval search is available.",
                    "requires_api_key": True,
                    "sources": self._matches_payload(question),
                },
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        try:
            answer = ask_nvidia(build_prompt(question, matches))
        except RuntimeError as error:
            self._send_json({"error": str(error)}, HTTPStatus.BAD_GATEWAY)
            return
        self._send_json({"answer": answer, "sources": self._matches_payload(question)})

    def log_message(self, format: str, *args: object) -> None:
        return


def create_server(host: str = "127.0.0.1", port: int = 8765) -> RagHTTPServer:
    server = RagHTTPServer((host, port), Handler)
    server.chunks = load_chunks(ROOT / "docs")
    server.ui_html = (ROOT / "webui.html").read_bytes()
    return server


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local NVIDIA RAG web interface")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    load_dotenv()
    server = create_server(args.host, args.port)
    print(f"NVIDIA RAG Lab: http://{args.host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
