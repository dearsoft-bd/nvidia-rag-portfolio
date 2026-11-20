# GPU-Accelerated AI Project Notes

## Project goal

The goal is a question-answering assistant that retrieves passages from a small local
document collection before generating an answer. Each factual answer should cite the
retrieved passage that supports it.

## Why retrieval matters

A language model does not automatically know which private documents are current or
authoritative. Retrieval supplies relevant context at question time and gives the user a
way to inspect the evidence behind an answer.

## Reducing unsupported answers

The project reduces unsupported answers with three safeguards:

1. It instructs the model to use only the retrieved context.
2. It requires numbered citations for factual claims.
3. It prints the retrieved source passages so a reader can verify the answer.

The safeguards reduce risk, but they do not make every generated answer correct. A useful
next step is an evaluation set that checks both citation quality and retrieval accuracy.

## GPU acceleration

GPU acceleration can reduce the time needed to train models and run parallel numerical
workloads. CUDA is a programming model for writing code that runs across NVIDIA GPUs.
NVIDIA NIM provides hosted model endpoints that applications can call through an API.

## Internship evidence

A strong portfolio entry should explain the problem, architecture, technical decisions,
test results, limitations, and how another developer can run the project.
