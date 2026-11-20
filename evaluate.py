#!/usr/bin/env python3
"""Run reproducible retrieval checks against the local document corpus."""

from __future__ import annotations

import argparse
import json

from evaluation import DEFAULT_CASES, evaluate_cases, summarize
from rag_cli import load_chunks, load_dotenv

from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the local retrieval baseline")
    parser.add_argument("--top-k", type=int, default=3, help="Number of passages retrieved")
    parser.add_argument("--json", action="store_true", help="Print a JSON report")
    args = parser.parse_args()

    load_dotenv()
    chunks = load_chunks(ROOT / "docs")
    results = evaluate_cases(chunks, DEFAULT_CASES, max(1, args.top_k))
    metrics = summarize(results)

    if args.json:
        print(
            json.dumps(
                {
                    "metrics": metrics,
                    "cases": [
                        {
                            "question": result.case.question,
                            "expected_source": result.case.expected_source,
                            "first_relevant_rank": result.first_relevant_rank,
                            "top_source": result.top_source,
                            "top_term_found": result.top_term_found,
                        }
                        for result in results
                    ],
                },
                indent=2,
            )
        )
    else:
        for index, result in enumerate(results, start=1):
            mark = "PASS" if result.first_relevant_rank else "MISS"
            print(f"{index}. {mark}: {result.case.question}")
            print(f"   expected: {result.case.expected_source}")
            print(f"   top:      {result.top_source or 'none'}")
        print("\nMetrics")
        print(f"  cases:          {metrics['cases']}")
        print(f"  hit rate@{args.top_k}: {metrics['hit_rate_at_k']:.3f}")
        print(f"  MRR:            {metrics['mrr']:.3f}")
        print(f"  term accuracy:  {metrics['term_accuracy']:.3f}")

    return 0 if metrics["hit_rate_at_k"] >= 0.75 and metrics["mrr"] >= 0.5 else 1


if __name__ == "__main__":
    raise SystemExit(main())
