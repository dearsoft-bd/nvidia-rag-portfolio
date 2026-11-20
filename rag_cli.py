#!/usr/bin/env python3
"""Small, dependency-free RAG demonstration for a portfolio project."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOKEN_RE = re.compile(r"[A-Za-z0-9_'-]+")


@dataclass(frozen=True)
class Chunk:
    source: str
    text: str
    tokens: tuple[str, ...]


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def load_chunks(docs_dir: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(docs_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
            continue
        resolved_path = path.resolve()
        try:
            source_path = resolved_path.relative_to(ROOT)
        except ValueError:
            source_path = resolved_path
        raw = path.read_text(encoding="utf-8").strip()
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", raw) if part.strip()]
        for index, paragraph in enumerate(paragraphs, start=1):
            tokens = tuple(tokenize(paragraph))
            if tokens:
                chunks.append(
                    Chunk(
                        source=f"{source_path}#paragraph-{index}",
                        text=paragraph,
                        tokens=tokens,
                    )
                )
    return chunks


def retrieve(chunks: list[Chunk], question: str, top_k: int = 4) -> list[tuple[float, Chunk]]:
    if not chunks:
        return []

    query_terms = set(tokenize(question))
    if not query_terms:
        return []

    document_frequency = Counter()
    for chunk in chunks:
        document_frequency.update(set(chunk.tokens))

    average_length = sum(len(chunk.tokens) for chunk in chunks) / len(chunks)
    results: list[tuple[float, Chunk]] = []
    k1, b = 1.5, 0.75

    for chunk in chunks:
        term_frequency = Counter(chunk.tokens)
        score = 0.0
        for term in query_terms:
            frequency = term_frequency[term]
            if not frequency:
                continue
            inverse_frequency = math.log(
                1 + (len(chunks) - document_frequency[term] + 0.5) / (document_frequency[term] + 0.5)
            )
            length_ratio = len(chunk.tokens) / average_length
            denominator = frequency + k1 * (1 - b + b * length_ratio)
            score += inverse_frequency * frequency * (k1 + 1) / denominator
        if score > 0:
            results.append((score, chunk))

    results.sort(key=lambda item: item[0], reverse=True)
    return results[:top_k]


def build_prompt(question: str, matches: list[tuple[float, Chunk]]) -> str:
    context = "\n\n".join(
        f"[{index}] Source: {chunk.source}\n{chunk.text}"
        for index, (_, chunk) in enumerate(matches, start=1)
    )
    return (
        "Answer the question using only the supplied context. "
        "Cite factual claims with square-bracket source numbers such as [1]. "
        "If the context is insufficient, say what is missing instead of guessing.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )


def ask_nvidia(prompt: str) -> str:
    api_key = os.getenv("NVIDIA_API_KEY")
    model = os.getenv("NVIDIA_MODEL")
    base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")

    if not api_key:
        raise RuntimeError("NVIDIA_API_KEY is not set. Run the --demo mode or configure .env first.")
    if not model:
        raise RuntimeError("NVIDIA_MODEL is not set. Choose a model ID from the current API Catalog.")

    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 700,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"NVIDIA API returned HTTP {error.code}: {body}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not reach the NVIDIA API: {error.reason}") from error

    try:
        return result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError(f"Unexpected API response: {json.dumps(result)[:1000]}") from error


def print_sources(matches: list[tuple[float, Chunk]]) -> None:
    print("\nSources")
    for index, (score, chunk) in enumerate(matches, start=1):
        preview = " ".join(chunk.text.split())
        if len(preview) > 260:
            preview = preview[:257].rstrip() + "..."
        print(f"[{index}] {chunk.source} (score {score:.3f})")
        print(f"    {preview}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local-retrieval RAG demo using NVIDIA NIM")
    parser.add_argument("--question", required=True, help="Question to answer")
    parser.add_argument("--top-k", type=int, default=4, help="Number of passages to retrieve")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Retrieve and print context without calling the NVIDIA API",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    chunks = load_chunks(ROOT / "docs")
    matches = retrieve(chunks, args.question, max(1, args.top_k))

    if not matches:
        print("No relevant passages found. Add documents to docs/ or rephrase the question.")
        return 1

    if args.demo:
        print("Demo retrieval only; no NVIDIA API call was made.")
        print_sources(matches)
        return 0

    try:
        answer = ask_nvidia(build_prompt(args.question, matches))
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    print(answer)
    print_sources(matches)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
