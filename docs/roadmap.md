# Project Roadmap

## PDF ingestion

Add PDF parsing while preserving the document page number as citation metadata.
Each extracted passage should identify both the file and the page number so a user
can verify the evidence.

## Retrieval comparison

Compare the keyword BM25 baseline with an embedding-based retriever. Use the same
evaluation questions and report hit rate at K, MRR, latency, and memory use.

## User interface

Build a small local interface that shows the generated answer beside the retrieved
passages. Add a clear warning when the model reports that context is insufficient.

## Deployment

Provide a container image only after the command-line and evaluation workflows are
stable. Keep secrets outside the image and document the required environment
variables.
