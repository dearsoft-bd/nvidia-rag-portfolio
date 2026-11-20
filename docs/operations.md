# Operations and API Configuration

## Environment variables

Store the NVIDIA API key in the local environment or in an ignored `.env` file. The
application loads simple `KEY=VALUE` entries from `.env` without overriding variables
that are already present in the shell environment.

Never commit the real API key. The repository should contain only `.env.example` with
placeholder values.

## Runtime flow

The command-line application loads local documents, tokenizes each paragraph, ranks
passages with a keyword-based BM25 baseline, and sends only the highest-ranked
passages to the configured NVIDIA chat-completion endpoint.

## Failure behavior

If the API key or model is missing, the application stops before making a network
request. If the API returns an HTTP error, the response body is included in the
command-line error so the operator can diagnose authentication or model problems.
