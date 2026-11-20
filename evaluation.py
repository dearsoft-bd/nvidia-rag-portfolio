"""Retrieval-quality evaluation for the local RAG baseline."""

from __future__ import annotations

from dataclasses import dataclass

from rag_cli import Chunk, retrieve


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    expected_source: str
    expected_term: str


@dataclass(frozen=True)
class CaseResult:
    case: EvaluationCase
    first_relevant_rank: int | None
    top_source: str | None
    top_term_found: bool


DEFAULT_CASES = (
    EvaluationCase(
        "How does the project reduce unsupported answers?",
        "docs/welcome.md",
        "safeguards",
    ),
    EvaluationCase(
        "Which environment variables configure the NVIDIA API?",
        "docs/operations.md",
        "environment",
    ),
    EvaluationCase(
        "What does mean reciprocal rank reward?",
        "docs/evaluation.md",
        "rank",
    ),
    EvaluationCase(
        "How can PDF page citations be added?",
        "docs/roadmap.md",
        "page",
    ),
)


def evaluate_cases(
    chunks: list[Chunk],
    cases: tuple[EvaluationCase, ...] = DEFAULT_CASES,
    top_k: int = 3,
) -> list[CaseResult]:
    results: list[CaseResult] = []
    for case in cases:
        matches = retrieve(chunks, case.question, top_k)
        first_rank = next(
            (
                rank
                for rank, (_, chunk) in enumerate(matches, start=1)
                if chunk.source.startswith(case.expected_source)
            ),
            None,
        )
        top_chunk = matches[0][1] if matches else None
        results.append(
            CaseResult(
                case=case,
                first_relevant_rank=first_rank,
                top_source=top_chunk.source if top_chunk else None,
                top_term_found=bool(
                    top_chunk and case.expected_term.lower() in top_chunk.text.lower()
                ),
            )
        )
    return results


def summarize(results: list[CaseResult]) -> dict[str, float]:
    if not results:
        return {"cases": 0, "hit_rate_at_k": 0.0, "mrr": 0.0, "term_accuracy": 0.0}
    hits = sum(result.first_relevant_rank is not None for result in results)
    reciprocal_ranks = sum(
        1.0 / result.first_relevant_rank
        for result in results
        if result.first_relevant_rank is not None
    )
    term_matches = sum(result.top_term_found for result in results)
    return {
        "cases": len(results),
        "hit_rate_at_k": hits / len(results),
        "mrr": reciprocal_ranks / len(results),
        "term_accuracy": term_matches / len(results),
    }
