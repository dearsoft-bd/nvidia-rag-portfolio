# DS-Pythone Two-Minute Demo Script

Target length: **1:55–2:00**

The demo uses only local retrieval and public project data. It must not display API
keys, private documents, browser profiles, shell history or account details.

## Scene 1 — Problem and outcome (0:00–0:15)

**Visual:** RAG Lab landing page with the four metric cards visible.

**Narration:**

> DS-Pythone is a local-first Python developer agent. It retrieves project evidence,
> shows its sources and measures retrieval quality with a reproducible evaluation.

## Scene 2 — Run a grounded search (0:15–0:45)

**Visual:** Enter “How does the project reduce unsupported answers?” and select
**Search passages**.

**Narration:**

> The question is converted into query terms and ranked against paragraph-sized
> chunks. The top evidence appears with document and paragraph identifiers, so the
> answer can be checked instead of accepted blindly.

**Highlight:** `docs/welcome.md#paragraph-7` and the three safeguards.

## Scene 3 — Evaluation (0:45–1:10)

**Visual:** Run `python3 evaluate.py`, then show the metric cards.

**Narration:**

> Five versioned questions define the current baseline. All five return the expected
> source at rank one: hit rate at three is one, MRR is one, and term accuracy is one.
> These are repository-level checks, not a claim of production benchmark results.

## Scene 4 — Tests and safety (1:10–1:35)

**Visual:** Run `python3 -m unittest discover -s tests -v`.

**Narration:**

> Eleven automated tests cover retrieval, evaluation, API request handling, the web
> endpoint and path-traversal protection. The agent is read-only, keeps credentials
> outside source control and treats retrieved text as untrusted evidence.

## Scene 5 — Architecture and close (1:35–1:55)

**Visual:** `docs/architecture.md`, then the project title and GitHub URL.

**Narration:**

> The architecture deliberately starts with an auditable BM25 baseline. The next
> step is to compare embedding retrieval and PDF page citations against the same
> evaluation set. DS-Pythone was created by Khandaker Readul Islam at DearSoft.

## Recording checklist

- Resolution: 1280×720 or 1440×900
- No terminal secrets or personal notifications
- Large readable font
- Cursor movement purposeful and slow
- No fabricated model response
- Final file: `docs/demo.mp4`
