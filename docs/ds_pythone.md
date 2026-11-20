# DS-Pythone Agent Design

DS-Pythone is a local-first developer agent. Its first version is deliberately small:
it retrieves evidence from the project documents, exposes only read-only tools, and
uses an NVIDIA-hosted OpenAI-compatible chat endpoint for grounded responses.

## Available tools

- Search allowlisted Markdown and text documents.
- Read a document only inside the configured `docs/` directory.
- Report retrieval metrics using the reproducible evaluation set.
- Report whether the model configuration is ready.

## Disabled by default

- Arbitrary shell execution.
- File writes outside the project.
- Uploading local documents or conversation history.
- Handling passwords, OTPs or API keys through the model.

The narrow tool surface makes failures and data access easier to review before adding
more autonomous capabilities.
