# Architecture and Trust Boundaries

## System context

DS-Pythone is a small retrieval-augmented generation application. It has two runtime
modes:

1. **Offline retrieval:** Load documents, create paragraph chunks, rank evidence and
   expose metrics without a network call.
2. **Grounded generation:** Build a prompt from the top-ranked evidence and send it to
   a configured OpenAI-compatible NVIDIA endpoint.

```text
CLI / web client
       |
       v
Read-only agent tools ------> evaluation metrics
       |
       v
Document loader -> paragraph chunks -> ranked evidence
                                         |
                                         v
                              grounded prompt builder
                                         |
                                         v
                              NVIDIA-compatible API
                                         |
                                         v
                              answer + source list
```

## Components

| Component | Responsibility |
|---|---|
| `rag_cli.py` | Document loading, chunking, ranking, prompt construction and API client |
| `ds_pythone.py` | Read-only agent interface and command handling |
| `webapp.py` / `webui.html` | Localhost search and evaluation interface |
| `evaluation.py` / `evaluate.py` | Deterministic retrieval-quality checks |
| `api_check.py` | Credential-safe model connectivity preflight |

## Data flow

1. Markdown and text files under `docs/` are read locally.
2. Paragraph boundaries define citation-sized chunks.
3. Query tokens are matched against the chunks with a BM25-style score.
4. Only the highest-ranked passages are included in a generation request.
5. The response is displayed beside the source references used to construct it.

Retrieved text is treated as evidence, never as executable instructions.

## Trust boundaries

- The model API is outside the local trust boundary.
- API credentials are loaded from the environment or an ignored `.env` file.
- The agent exposes no arbitrary shell or write capability.
- Document reads are constrained to the project's `docs/` directory.
- Secrets and private documents must never be committed.
- The UI binds to localhost by default.

## Failure behavior

- Missing credentials stop the hosted-generation path before a request is sent.
- API failures are returned as explicit runtime errors.
- Missing or weak evidence produces no invented source citations.
- The evaluation command exits non-zero if retrieval quality drops below baseline.

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

## Trade-offs

The keyword retriever is small, deterministic and easy to audit, but it does not
capture semantic similarity as reliably as embeddings. Keeping the baseline makes it
possible to compare future embedding or hybrid retrieval without changing the
evaluation contract.

## Scaling path

- Add embedding retrieval and compare every change against the same cases.
- Persist chunk metadata for PDF page citations.
- Add latency and memory measurements.
- Introduce a container only after CLI and web workflows are stable.
