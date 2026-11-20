# Architecture Decisions

## Dependency-free baseline

The first version uses only the Python standard library. This keeps setup fast and
makes the retrieval logic easy to inspect during an interview or code review.

## Paragraph-level chunks

Each Markdown or text paragraph becomes one retrieval unit. Paragraph boundaries
preserve author intent better than arbitrary fixed-length slices and keep citation
previews readable.

## Lexical retrieval

The BM25-style ranker rewards question terms that occur frequently in a passage
while accounting for document frequency and passage length. It provides a
reproducible baseline before introducing embeddings or a vector database.

## Grounded generation

Only the top-ranked passages are included in the model prompt. The prompt requires
numbered citations and tells the model to report missing context instead of
guessing. Sources are printed after the answer for independent verification.
