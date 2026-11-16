# Epic 1 summary — Initiation and architecture

Written 2026-11-17. This page explains what Epic 1 produced, story by story, and how each
piece is used by the rest of the project. It is a summary; the linked documents hold the
detail.

## What the project is

Ask the Circular lets a job seeker upload a Bangladeshi job circular (PDF or image, Bangla
or English) and get three things: a fact card (posts, deadline, age limit, fee, how to
apply), a per-post eligibility verdict against their CV, and a question-and-answer chat.
Every answer must cite the passage it came from, and the whole thing must cost nothing to
build and run.

## What Epic 1 was for

Epic 1 wrote no user-facing features. Its job was to remove the big unknowns before
building: can scanned Bangla circulars be read at all, which free LLM is good enough, will
it fit on a free server, and what exactly will the frontend and backend say to each other.
Each answer is recorded as a short decision record (ADR) in `_context/decisions/`.

## Story by story

### 1.1 Repo skeleton
- **Done:** folder layout, a FastAPI backend with a `/health` route, a React + TypeScript
  frontend, `.env.example`, MIT licence, and a GitHub Actions job that lints and tests both
  sides on every push.
- **Why it matters later:** every later story has a place to put its code, and broken code
  is caught automatically.

### 1.2 Test corpus
- **Done:** 15 real circulars collected from official government websites (12 scanned, 3
  digital, 8 with more than one post, 2 in English). Each has a label file with the correct
  fact card. `eval/corpus.py` checks the labels and re-downloads the PDFs, which are not
  stored in the repository.
- **Not finished:** the labels are drafts written by an AI assistant and still need the
  owner's check. No circular in the old Bijoy font encoding was found; the target was two.
- **Why it matters later:** this is the yardstick. Every accuracy number in the project is
  measured against these 15 files. Detail: `eval/README.md`.

### 1.3 Format spike
An experiment on the 15 circulars to choose the tools. Detail: `docs/SPIKE.md`.

| Question | Finding | Decision |
|---|---|---|
| Can we tell file types apart? | 15 of 15 classified correctly. Only 2 files had a usable text layer; some scans carry a junk one | detection rules in SPIKE §2 |
| Can scanned Bangla be read? | Tesseract recovered 98% of the labelled facts | ADR-005: Tesseract, 200 dpi |
| What about Bijoy files? | The available converter made spelling errors; reading the rendered page works | ADR-006: treat as a scan (provisional) |
| Which LLM? | Small local models got 22–60% of fact-card fields right; Groq's `qwen/qwen3.8-27b` got 91% | ADR-007 |
| Does it fit in 512 MB? | Server plus one OCR page is about 230 MB | ADR-008 |

- **Not finished:** the memory of the embedding model (used for search) was not measured.
- **Why it matters later:** Epic 3 (reading circulars) can be built with known tools and
  known accuracy instead of guesses. The spike also showed that the free LLM tier allows
  only about 8,000 tokens per minute, which shaped Story 1.4.

### 1.4 Agent design
- **Done:** the design of the question-answering loop: route the question, gather the
  relevant passages, draft an answer with citations, check every sentence against the
  sources, then revise or say "not clearly stated in the circular". The prompts for each
  step are written and were tried on real circular text: 10 of 10 test questions behaved
  correctly, including two prompt-injection attempts. Detail: `docs/AGENT.md`.
- **Key decision (ADR-009):** each step uses a different free model so that no single
  model's per-minute allowance is exhausted by one question.
- **Why it matters later:** Epic 4 (the chat) implements this design directly. Known limit:
  on the free tier the app can serve about two questions per minute, enough for a demo.

### 1.5 API contracts
- **Done:** the exact shape of every request and response is fixed: 15 endpoints and 41
  data schemas. The endpoints exist as placeholders that answer "not built yet". A test
  fails if the API ever drifts from the saved contract (`docs/openapi.json`), and the
  frontend's TypeScript types are generated from that same file. Detail: `docs/API.md`.
- **Why it matters later:** frontend and backend can be built separately, by different
  tools in different sessions, and still fit together. Epics 2–4 fill in the placeholders
  one by one.

## Decisions made in Epic 1

| ADR | Decision |
|---|---|
| 005 | Tesseract (`ben+eng`, 200 dpi) reads every file without a usable text layer |
| 006 | Bijoy-encoded PDFs are read through OCR for now (provisional) |
| 007 | `qwen/qwen3.8-27b` on Groq in production; `gemma3:4b` on Ollama for local development |
| 008 | Memory plan for the 512 MB server; the embedding model is still to be measured |
| 009 | One model per agent step, a token limit per call, at most 5 LLM calls per question |
| 010 | The API contract is frozen as an OpenAPI snapshot guarded by a test |

ADRs 001–004 (own login system, hand-written agent, CV handling, no Node gateway) were made
before Epic 1 started.

## What is still open

| Item | Who | Needed before |
|---|---|---|
| Check the 15 draft labels against the PDFs | owner | any accuracy number is quoted publicly |
| Supply at least 2 Bijoy circulars | owner | ADR-006 can be confirmed |
| Measure the embedding model's memory (needs a model download) | owner's go-ahead | Story 3.1 |
| Increment 1: `python eval/run_eval.py --extract-only` prints baseline accuracy | next session | Epic 1 is formally closed |

## How Epic 1 feeds the next epics

| Epic | What it builds | What it takes from Epic 1 |
|---|---|---|
| 2 Accounts and profile | sign-up, consent, CV → profile | the auth, consent and profile endpoints and schemas (1.5); CI (1.1) |
| 3 Circular understanding | ingestion, fact card, eligibility | detection rules and OCR settings (1.3); the fact-card schema (1.5); the corpus to measure against (1.2) |
| 4 Agentic Q&A | retrieval, the agent loop, chat UI | the loop design, prompts and budgets (1.4); the ask-stream contract (1.5); the chosen models (1.3) |

## Where to read more

| Topic | File |
|---|---|
| Current status and next actions | `IMPLEMENTATION.md` |
| Rules and intent | `_context/SOP.md` |
| System design | `docs/ARCHITECTURE.md` |
| Spike measurements | `docs/SPIKE.md` |
| Agent design | `docs/AGENT.md` |
| API contract | `docs/API.md` |
| Plan | `ROADMAP.md` |
