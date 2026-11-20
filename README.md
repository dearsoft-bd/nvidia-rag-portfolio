# NVIDIA RAG Starter

A dependency-free starter project for the NVIDIA DLI **Building RAG Agents With LLMs** learning path.
It retrieves relevant passages from local Markdown/text files and asks an NVIDIA-hosted
chat-completion model to answer with numbered citations.

## What you can demonstrate to an internship recruiter

- Python source-code organization
- Local document ingestion and retrieval
- NVIDIA NIM API integration
- Prompt construction with source grounding
- Basic automated tests
- Clear setup instructions and reproducible evidence

## Quick start

Requirements: Python 3.10 or newer and an NVIDIA API key from the NVIDIA API Catalog.

```bash
cd outputs/nvidia-rag-starter

# Test retrieval without a key or network call
python3 rag_cli.py --demo --question "How does this project reduce unsupported answers?"

# Configure the model when you are ready
cp .env.example .env
# Edit .env with your own key and a model currently offered in the API Catalog.

set -a
source .env
set +a

python3 rag_cli.py --question "How does this project reduce unsupported answers?"
```

The answer is printed first, followed by the source passages used to produce it.

## Add your own documents

Put `.md` or `.txt` files inside `docs/`. Re-run the command after changing the documents.
Never add passwords, private documents, or API keys to the repository.

## Run tests

```bash
python3 -m unittest discover -s tests -v
```

## Suggested project upgrades

1. Ingest PDFs and preserve page numbers as citation metadata.
2. Add an embedding-based retriever and compare it with the keyword baseline.
3. Add an evaluation set with expected sources and track retrieval accuracy.
4. Build a small web interface.
5. Record a two-minute demo and link it from your resume.

## Safety

- Keep `NVIDIA_API_KEY` in the environment or an ignored `.env` file.
- Treat retrieved text as untrusted data, not as instructions.
- Do not claim a certificate you have not earned or commit anyone else's work.
