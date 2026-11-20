# Retrieval Evaluation

## Evaluation set

Each evaluation case contains a question, the expected document source, and a term
that should appear in the highest-ranked passage. The set is intentionally small so
it can run without external services.

## Metrics

Hit rate at K measures whether at least one relevant passage appears among the first
K retrieved passages. Mean reciprocal rank, or MRR, rewards systems that place the
first relevant result near the top and gives zero credit when no relevant result is
retrieved.

## Reproducibility

Run the evaluation command after changing the corpus or ranking logic. Record the
metrics in the project README whenever the retrieval approach changes.
