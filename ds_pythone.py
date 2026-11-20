#!/usr/bin/env python3
"""DS-Pythone: a small, local-first developer agent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from evaluation import DEFAULT_CASES, evaluate_cases, summarize
from rag_cli import (
    ROOT,
    Chunk,
    ask_nvidia,
    build_prompt,
    load_chunks,
    load_dotenv,
    retrieve,
)

PLACEHOLDER_KEYS = {"", "nvapi-REPLACE_WITH_YOUR_KEY", "nvapi-replace-me"}


@dataclass
class AgentTools:
    """Allowlisted, read-only tools available to DS-Pythone."""

    docs_dir: Path = ROOT / "docs"
    chunks: list[Chunk] = field(default_factory=list)
    history: list[tuple[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.chunks:
            self.chunks = load_chunks(self.docs_dir)

    def status(self) -> dict:
        api_ready = os.getenv("NVIDIA_API_KEY", "") not in PLACEHOLDER_KEYS
        return {
            "name": "DS-Pythone",
            "documents": len(
                [
                    path
                    for path in self.docs_dir.rglob("*")
                    if path.is_file() and path.suffix.lower() in {".md", ".txt"}
                ]
            ),
            "chunks": len(self.chunks),
            "api_configured": api_ready,
            "model": os.getenv("NVIDIA_MODEL", ""),
            "tools": ["search_docs", "read_doc", "evaluation_metrics"],
        }

    def search_docs(self, query: str, top_k: int = 4) -> list[dict]:
        query = query.strip()
        if not query:
            return []
        matches = retrieve(self.chunks, query, max(1, min(top_k, 8)))
        return [
            {
                "rank": rank,
                "score": round(score, 4),
                "source": chunk.source,
                "text": " ".join(chunk.text.split()),
            }
            for rank, (score, chunk) in enumerate(matches, start=1)
        ]

    def read_doc(self, source: str) -> str:
        """Read only Markdown/text documents inside the configured docs directory."""
        raw_path = source.split("#", 1)[0]
        candidate = (ROOT / raw_path).resolve()
        docs_root = self.docs_dir.resolve()
        if docs_root not in candidate.parents:
            candidate = (self.docs_dir / raw_path).resolve()
        if docs_root not in candidate.parents:
            raise ValueError("DS-Pythone cannot read files outside docs/")
        if candidate.suffix.lower() not in {".md", ".txt"} or not candidate.is_file():
            raise ValueError("Only existing Markdown/text documents can be read")
        return candidate.read_text(encoding="utf-8")

    def metrics(self) -> dict[str, float]:
        return summarize(evaluate_cases(self.chunks, DEFAULT_CASES, top_k=3))

    def ask(self, question: str) -> str:
        question = question.strip()
        if not question:
            raise ValueError("Enter a non-empty question")
        matches = retrieve(self.chunks, question, 4)
        if not matches:
            return "I could not find relevant context in the local documents."
        if os.getenv("NVIDIA_API_KEY", "") in PLACEHOLDER_KEYS:
            raise RuntimeError(
                "NVIDIA API key is not configured. Use /search for offline retrieval."
            )

        memory = ""
        if self.history:
            recent = "\n".join(
                f"User: {prior_question}\nDS-Pythone: {prior_answer}"
                for prior_question, prior_answer in self.history[-3:]
            )
            memory = f"\nConversation memory:\n{recent}\n"

        prompt = (
            "You are DS-Pythone, a careful developer agent. "
            "Use only the supplied local context for project claims. "
            "Never invent file contents, tests, credentials or command results. "
            "Cite sources using [1], [2] notation and clearly state missing information."
            f"{memory}\n\n{build_prompt(question, matches)}"
        )
        answer = ask_nvidia(prompt)
        self.history.append((question, answer))
        return answer


def print_sources(items: list[dict]) -> None:
    print("\nSources")
    for item in items:
        preview = item["text"]
        if len(preview) > 260:
            preview = preview[:257].rstrip() + "..."
        print(f"[{item['rank']}] {item['source']} (score {item['score']:.3f})")
        print(f"    {preview}")


def print_help() -> None:
    print(
        """Commands
  /help              Show this help
  /status            Show agent and API status
  /search <query>    Search local project documents
  /read <source>     Read an allowlisted docs/ file
  /metrics           Evaluate retrieval quality
  /ask <question>    Ask the configured NVIDIA model
  /clear             Clear conversation memory
  /quit              Exit

Any other text is treated as a question."""
    )


def handle_line(agent: AgentTools, line: str, offline: bool) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped in {"/quit", "/exit"}:
        return False
    if stripped == "/help":
        print_help()
        return True
    if stripped == "/status":
        print(json.dumps(agent.status(), indent=2))
        return True
    if stripped == "/metrics":
        print(json.dumps(agent.metrics(), indent=2))
        return True
    if stripped == "/clear":
        agent.history.clear()
        print("Conversation memory cleared.")
        return True
    if stripped.startswith("/search "):
        items = agent.search_docs(stripped.removeprefix("/search "))
        if not items:
            print("No relevant passages found.")
        else:
            print(f"Found {len(items)} passages.")
            print_sources(items)
        return True
    if stripped.startswith("/read "):
        try:
            print(agent.read_doc(stripped.removeprefix("/read ")))
        except ValueError as error:
            print(f"Error: {error}", file=sys.stderr)
        return True
    if stripped.startswith("/ask "):
        question = stripped.removeprefix("/ask ")
    else:
        question = stripped

    if offline:
        items = agent.search_docs(question)
        print("Offline retrieval result; no model call was made.")
        print_sources(items)
        return True
    try:
        answer = agent.ask(question)
    except (RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return True
    print(answer)
    print_sources(agent.search_docs(question))
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DS-Pythone local-first developer agent")
    parser.add_argument("-q", "--question", help="Run one question and exit")
    parser.add_argument("--offline", action="store_true", help="Retrieval only; no API calls")
    parser.add_argument("--status", action="store_true", help="Print agent status and exit")
    parser.add_argument("--metrics", action="store_true", help="Print evaluation metrics and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv()
    agent = AgentTools()

    if args.status:
        print(json.dumps(agent.status(), indent=2))
        return 0
    if args.metrics:
        print(json.dumps(agent.metrics(), indent=2))
        return 0
    if args.question:
        return 0 if handle_line(agent, args.question, args.offline) else 1

    print("DS-Pythone — local-first developer agent")
    print("Type /help for commands. No shell or write tools are enabled.")
    while True:
        try:
            line = input("DS-Pythone> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not handle_line(agent, line, args.offline):
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
