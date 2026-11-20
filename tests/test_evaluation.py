import unittest

from evaluation import EvaluationCase, evaluate_cases, summarize
from rag_cli import Chunk, tokenize


def make_chunk(source: str, text: str) -> Chunk:
    return Chunk(source=source, text=text, tokens=tuple(tokenize(text)))


class EvaluationTests(unittest.TestCase):
    def test_metrics_credit_relevant_result(self) -> None:
        chunks = [
            make_chunk("docs/other.md#paragraph-1", "unrelated material"),
            make_chunk("docs/target.md#paragraph-1", "relevant evaluation material"),
        ]
        cases = (
            EvaluationCase(
                question="Where is the relevant evaluation material?",
                expected_source="docs/target.md",
                expected_term="evaluation",
            ),
        )

        results = evaluate_cases(chunks, cases, top_k=2)
        metrics = summarize(results)

        self.assertEqual(results[0].first_relevant_rank, 1)
        self.assertEqual(metrics["hit_rate_at_k"], 1.0)
        self.assertEqual(metrics["mrr"], 1.0)
        self.assertEqual(metrics["term_accuracy"], 1.0)

    def test_miss_returns_zero_metrics(self) -> None:
        chunks = [make_chunk("docs/other.md#paragraph-1", "unrelated material")]
        cases = (
            EvaluationCase(
                question="Where is the missing material?",
                expected_source="docs/target.md",
                expected_term="missing",
            ),
        )

        metrics = summarize(evaluate_cases(chunks, cases, top_k=1))

        self.assertEqual(metrics["hit_rate_at_k"], 0.0)
        self.assertEqual(metrics["mrr"], 0.0)
        self.assertEqual(metrics["term_accuracy"], 0.0)


if __name__ == "__main__":
    unittest.main()
