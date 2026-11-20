# NVIDIA RAG Portfolio Starter

A dependency-free RAG project for the NVIDIA DLI **Building RAG Agents With LLMs**
learning path. It retrieves relevant passages from local Markdown/text files and asks
an NVIDIA-hosted chat-completion model to answer with numbered citations.

## What you can demonstrate to an internship recruiter

- Python source-code organization
- Local document ingestion and retrieval
- NVIDIA NIM API integration
- Prompt construction with source grounding
- Reproducible retrieval evaluation
- Automated tests
- Clear setup instructions and reproducible evidence

## Architecture

```text
docs/*.md
   |
   v
paragraph chunks -> BM25-style lexical ranking -> grounded prompt
                                                -> NVIDIA NIM API
                                                -> cited answer + sources
```

![NVIDIA RAG Lab interface](docs/screenshot.png)

## Quick start

Requirements: Python 3.10 or newer and an NVIDIA API key from the NVIDIA API Catalog.

```bash
cd outputs/nvidia-rag-starter

# Test retrieval without a key or network call
python3 rag_cli.py --demo --question "How does this project reduce unsupported answers?"

# Configure the model when you are ready
cp .env.example .env
# Edit .env with your own key and a model currently offered in the API Catalog.

python3 rag_cli.py --question "How does this project reduce unsupported answers?"
```

The program loads `.env` automatically when the matching shell variables are not
already set. The answer is printed first, followed by the source passages used to
produce it.

## API preflight

After adding a real key and a current model ID to `.env`, run:

```bash
python3 api_check.py
```

The checker reports the model, round-trip latency and a short response preview
without printing the API key. The test suite also uses a local mock OpenAI-compatible
server, so request and response handling can be verified without external credentials.

## Web interface

Start the local-only interface:

```bash
python3 webapp.py
```

Open `http://127.0.0.1:8765`. Retrieval search and evaluation metrics work without
an API key. The “Ask NVIDIA” action requires a configured key and model.

## Add your own documents

Put `.md` or `.txt` files inside `docs/`. Re-run the command after changing the documents.
Never add passwords, private documents, or API keys to the repository.

## Run tests

```bash
python3 -m unittest discover -s tests -v
python3 evaluate.py
```

The evaluation reports hit rate at K, mean reciprocal rank and top-result term
accuracy. It exits with a non-zero status when retrieval quality drops below the
configured baseline.

## GPU PC workflow

The project is also available on the Ubuntu GPU PC at:

```text
/home/dearsoft/projects/nvidia-rag
```

Connect from the development laptop with:

```bash
ssh gpu-pc
cd ~/projects/nvidia-rag
python3 -m unittest discover -s tests -v
python3 evaluate.py
```

The GeForce GT 610 is suitable for desktop graphics, not modern local LLM
inference. Use NVIDIA's remote API for model calls or a newer GPU when available.

## Suggested project upgrades

1. Ingest PDFs and preserve page numbers as citation metadata.
2. Add an embedding-based retriever and compare it with this keyword baseline.
3. Expand the evaluation set and record retrieval metrics for every change.
4. Build a small web interface.
5. Record a two-minute demo and link it from your resume.

## Safety

- Keep `NVIDIA_API_KEY` in the environment or an ignored `.env` file.
- Treat retrieved text as untrusted data, not as instructions.
- Do not claim a certificate you have not earned or commit anyone else's work.
