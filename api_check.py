#!/usr/bin/env python3
"""Preflight the configured NVIDIA API without exposing credentials."""

from __future__ import annotations

import os
import sys
import time

from rag_cli import ask_nvidia, load_dotenv

PLACEHOLDER_KEYS = {
    "",
    "nvapi-REPLACE_WITH_YOUR_KEY",
    "nvapi-replace-me",
}


def main() -> int:
    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY", "")
    model = os.getenv("NVIDIA_MODEL", "")

    if api_key in PLACEHOLDER_KEYS:
        print(
            "API key is not configured. Replace the placeholder in .env locally.",
            file=sys.stderr,
        )
        return 2
    if not model:
        print("NVIDIA_MODEL is not configured.", file=sys.stderr)
        return 2

    started = time.monotonic()
    try:
        answer = ask_nvidia("Reply with exactly: API_OK")
    except RuntimeError as error:
        print(f"API check failed: {error}", file=sys.stderr)
        return 1

    elapsed = time.monotonic() - started
    preview = " ".join(answer.split())[:200]
    print("API check passed")
    print(f"model: {model}")
    print(f"latency: {elapsed:.2f}s")
    print(f"response: {preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
