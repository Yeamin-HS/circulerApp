# Roadmap — Epic → Story → Increment

## v1 (days 1–3): core demo

### Epic 1: Initiation & architecture (Phase 1)
| Story | Done when |
|---|---|
| 1.1 Repo skeleton | folders, CLAUDE.md, SOP, .env.example, licence, CI lint job |
| 1.2 Test corpus | 12–15 circulars collected; fact-card labels written by hand |
| 1.3 Format spike | each circular run through extract / OCR / Bijoy conversion; quality table; OCR, converter, model and RAM decisions logged as ADRs |
| 1.4 Agent design | state diagram and prompts drafted (section 6 of ARCHITECTURE.md) |
| 1.5 API contracts | Pydantic schemas and the endpoint list frozen |
**Increment 1:** `python eval/run_eval.py --extract-only` prints baseline field accuracy.

### Epic 2: Accounts and profile
| Story | Done when |
|---|---|
| 2.1 Auth | register and login, argon2, JWT, role guard, JWT storage decision |
| 2.2 Consent + delete | consent stored; `DELETE /me` cascades through all tables |
| 2.3 CV → profile | upload, extraction, review/edit screen, confirm, file deleted |
**Increment 2:** a user can sign up, upload a CV, and confirm their profile in the UI.

### Epic 3: Circular understanding
| Story | Done when |
|---|---|
| 3.1 Ingestion | detect → text → normalise → chunk → embed → store |
| 3.2 Fact card | evidence-validated extraction; UI card with clickable sources |
| 3.3 Eligibility | rules engine + LLM subject match; per-post verdict UI |
**Increment 3:** upload a circular → fact card + "eligible for X of Y posts".

### Epic 4: Agentic Q&A
| Story | Done when |
|---|---|
| 4.1 Retrieval | hybrid search with RRF |
| 4.2 Agent loop | route → gather → draft → critique → revise/abstain, with a call budget |
| 4.3 Chat UI | SSE streaming, citations, "verifying…" state |
**Increment 4:** v1 deployed on Vercel + Render + Neon; demo video recorded.

## v1.1 (days 4–5): depth and evidence
| Story | Done when |
|---|---|
| 5.1 Dashboard | "My circulars" sorted by deadline with verdict badges |
| 5.2 Admin | shared circulars, metrics page |
| 5.3 Reasoning panel | route, chunks and critique visible per answer |
| 5.4 Evaluation | full eval run + ablation table in the README |
| 5.5 Polish | mobile pass, dark mode, cold-start UX, README with architecture diagram |
**Increment 5:** portfolio-ready repository with measured results.
