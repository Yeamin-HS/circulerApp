# IMPLEMENTATION LOG — handoff file between Claude Code and Codex

Read this first. Update it at the end of every session, and before a session runs out of tokens.

## Current state
- Active story: 2.2 Consent + delete (not started). 2.1 Auth is done. Epic 1 stories 1.1, 1.3, 1.4, 1.5 are done; 1.2 waits on the owner (label verification, Bijoy samples); Increment 1 (`eval/run_eval.py --extract-only`) is not built. 1.2 stays open on the owner's side (label verification, Bijoy samples).
- Last tool used: Claude Code
- Last updated: 2026-11-17
- Branch: main
- Remote: https://github.com/Yeamin-HS/circulerApp (public)

## Next 3 actions
1. Owner: check each `eval/labels/*.json` against its PDF, fix errors, set `"verified": true`
2. Owner: add at least 2 Bijoy/SutonnyMJ circulars (none found on the 71 gov.bd sites swept) with labels; then Story 1.2 closes
3. Increment 1: make `python eval/run_eval.py --extract-only` print baseline field accuracy (reuse the scoring in `eval/spike.py`, output the frozen `FactCard`)
4. Story 2.2: `POST /me/consent` and `DELETE /me` (cascade), with a consent screen and a delete-account button in the UI
5. Before Story 3.1: measure the embedding model's memory (ADR-008); needs the model files, which the owner declined to download during the spike

## Done (newest first)
| Date | Tool | Story | What changed | Files |
|---|---|---|---|---|
| 2026-11-17 | Claude Code | 2.1 | Auth: register, login and `GET /me` live; argon2id hashes, 60-minute HS256 JWT, user and role loaded from the DB per request, admin guard, per-IP limit on auth routes, CORS; SQLAlchemy `users` table with SQLite fallback; frontend sign-in / sign-up screens with session kept per ADR-012. 20 backend tests pass. Contract changed on purpose: 429 on register and login. Local only, not committed | `backend/app/core/{config,security,ratelimit}.py`, `backend/app/db/{session,models}.py`, `backend/app/api/{auth,deps,me}.py`, `backend/app/main.py`, `backend/tests/{conftest,test_auth,test_contract}.py`, `backend/pyproject.toml`, `frontend/src/{api,hooks,components,pages}/*`, `frontend/src/App.tsx`, `frontend/src/index.css`, `frontend/vite.config.ts`, `frontend/index.html`, `docs/openapi.json`, `frontend/src/types/api.d.ts`, `docs/API.md`, `docs/ARCHITECTURE.md`, `.env.example`, `.gitignore`, ADR-011, ADR-012 |
| 2026-11-17 | Claude Code | Epic 1 | Plain-language summary of Epic 1, story by story, with open items and how it feeds Epics 2–4. Local only, not committed | `docs/EPIC-1-SUMMARY.md` |
| 2026-11-17 | Claude Code | 1.5 | API contract frozen: 41 Pydantic schemas, 15 endpoints as stub routes (501), one error shape, OpenAPI snapshot with a guard test, generated frontend types, API document. Local only, not committed | `backend/app/core/schemas.py`, `backend/app/core/errors.py`, `backend/app/api/{auth,me,circulars,deps}.py`, `backend/app/main.py`, `backend/tests/test_contract.py`, `backend/pyproject.toml`, `docs/API.md`, `docs/openapi.json`, `frontend/src/types/api.d.ts`, `frontend/package.json`, `_context/decisions/ADR-010-api-contract-v1.md`, `docs/ARCHITECTURE.md` |
| 2026-11-17 | Claude Code | 1.4 | Agent design: state diagram, states, call and token budgets, data shapes; prompts for route, draft, critique, revise and subject check; smoke test on Groq passes 10/10 questions, critic 1/1, subject 3/3 after one round of prompt fixes. Local only, not committed | `docs/AGENT.md`, `backend/app/agent/prompts.py`, `backend/tests/test_prompts.py`, `eval/agent_smoke.py`, `_context/decisions/ADR-009-agent-budget-and-roles.md`, `docs/ARCHITECTURE.md` |
| 2026-11-17 | Claude Code | 1.3 | Groq benchmark on the 3 chat models the free key offers: `qwen/qwen3.8-27b` 91%, `gpt-oss-120b` 87%, `gpt-oss-20b` 83% of fields; production model chosen (ADR-007). Spike script gained Groq retry on 429. Local only, not committed | `eval/spike.py`, `docs/SPIKE.md`, `_context/decisions/ADR-007-llm-models.md`, `docs/ARCHITECTURE.md` |
| 2026-11-16 | Claude Code | 1.3 | Format spike: type detection 15/15; Tesseract 200 dpi recovers 98% of labelled facts on scans; Bijoy routed through OCR; local LLMs benchmarked (best `gemma3:4b`, 60% of fields); memory measured except embeddings. Results in docs/SPIKE.md. Local only, not committed | `eval/spike.py`, `docs/SPIKE.md`, `_context/decisions/ADR-005..008`, `backend/pyproject.toml` (`spike` extra), `docs/ARCHITECTURE.md`, `eval/README.md` |
| 2026-11-16 | Claude Code | 1.2 | 15 real circulars downloaded from official gov.bd sites (3 digital, 12 scanned, 8 multi-post, 2 English); draft fact-card label per circular; label checker + re-download script; label format documented. Local only, not committed | `eval/labels/*.json`, `eval/corpus.py`, `eval/README.md`, `eval/circulars/*.pdf` (gitignored) |
| 2026-11-16 | Claude Code | 1.1 | Added MIT licence; Story 1.1 closed | `LICENSE` |
| 2026-11-16 | Claude Code | 1.1 | Repo skeleton: backend package folders, FastAPI app with `/health` + test, Vite React-TS app (demo content trimmed), eval folders + stub runner, `.env.example`, `.gitignore`, CI lint workflow; first commit pushed to GitHub | `backend/`, `frontend/`, `eval/`, `.env.example`, `.gitignore`, `.github/workflows/lint.yml` |

## In progress / half-done
- Story 2.1 work is uncommitted: the owner adds, commits and pushes manually.
- Live routes: `/health`, `/auth/register`, `/auth/login`, `GET /me`. Every other route is still a stub returning 501.
- `has_confirmed_profile` is always false until Story 2.3.
- ADR-008 (embedding memory) has an open part; see "Next actions".
- All 15 labels are AI drafts (`"verified": false`). They are not ground truth until the owner checks them.
- `eval/run_eval.py` is an intentional stub (exits 1) until Increment 1.

## Known issues / blockers
- Corpus gap: 0 Bijoy circulars (target ≥ 2). `python eval/corpus.py check` reports it as `GAP`.
- The sign-in screens were checked by type-check, lint and build, and the API flow by curl against a running server; nobody has clicked through them in a browser yet. There are no frontend tests.
- No way to create an admin from the app: set `role = 'admin'` on the user row by hand. No password reset (ADR-001).
- The rate limit is in memory, per process; it resets on restart.
- No Neon database yet: auth has only run on SQLite (ADR-011).
- Agent capacity on the free tier is about 2 questions per minute and under 1,000 a day for the whole app (docs/AGENT.md §5): enough for a demo only.
- The agent smoke test is 14 hand-picked checks on 2 circulars with stand-in retrieval; it does not prove NFR-02.
- Groq free tier: about 8,000 tokens per minute per model. A long circular nearly fills it and one request got HTTP 413. Story 3.2 must split extraction into smaller calls and retry on 429.
- Local models are for wiring only (best `gemma3:4b`: 73% digital, 57% scanned); judge accuracy on the Groq model.
- All spike scores are against unverified draft labels.
- OCR speed on Render's CPU is unmeasured (2.2 s/page on the Mac).
- For Story 3.1/3.2: OCR loses table columns; exact quote matching will fail on OCR text (use fuzzy matching); `c05` page 2 is a different notice with its own post table.
- Findings for Story 1.5: age limit and fee often differ per post, and a second apply URL can appear. `FactCard` has one `age_limit`; the labels add `posts[].age_limit` and `apply_mode`.
- pytest prints a Starlette deprecation warning about `httpx` in the test client; harmless for now.

## Decisions made this session
- ADR-011 SQLAlchemy 2 + psycopg; SQLite file when `DATABASE_URL` is empty; `create_all` until Alembic arrives in Story 3.1.
- ADR-012 (provisional, owner to confirm) JWT in memory mirrored to `sessionStorage`.
- Minor, no ADR: frontend has no router library; `App.tsx` switches screens on auth state. Vite reads the repo-root `.env` (`envDir: '..'`).
- New runtime dependencies: `sqlalchemy`, `psycopg[binary]`, `argon2-cffi`, `pyjwt` (all free).
- ADR-010 API contract v1 frozen as `docs/openapi.json`; changing it means `UPDATE_OPENAPI=1 pytest tests/test_contract.py`, then `npm run types`, then a note here. Changes from the ARCHITECTURE draft are in docs/API.md §6.
- Minor, no ADR: frontend types are generated with a pinned `npx openapi-typescript@7.13.0` rather than a dev dependency, because its peer range (TypeScript 5) conflicts with the project's TypeScript 7.
- New runtime dependencies: `email-validator`, `python-multipart` (both free, needed by FastAPI for email fields and uploads).
- ADR-009 one Groq model per agent role (route `gpt-oss-20b`, draft/revise `qwen3.8-27b`, critique `gpt-oss-120b`), token cap per call, Python citation lint before critique, fact-card fast path.
- Agent budget: ARCHITECTURE said 5 calls and 2 revisions, which cannot both be used in full (7 calls); kept the 5-call cap (docs/AGENT.md §4).
- ADR-005 Tesseract `ben+eng` at 200 dpi, no OpenCV · ADR-006 Bijoy through OCR (provisional) · ADR-007 `qwen/qwen3.8-27b` on Groq for production (fallback `openai/gpt-oss-120b`), `gemma3:4b` for dev · ADR-008 memory plan, embedding part open.
- Owner rule: no model downloads from Hugging Face without asking first.
- Owner rule: commit messages carry no `Co-Authored-By` AI trailer (keeps AI tools out of the GitHub contributors list).
- Minor, no ADR: plain `venv` + `pip` with setuptools (no `uv`); `ruff` for Python lint/format.
- Minor, no ADR: the current Vite `react-ts` template ships `oxlint` instead of ESLint; kept as is.
- `eval/circulars/*` and `eval/results/*` are gitignored (ARCHITECTURE §2: licence unclear).

## Environment notes
- Required env vars: see .env.example. Real values go in `.env` only (gitignored); never in `.env.example`. A `.env` with the owner's Groq key exists locally.
- Spike with Groq: `set -a; source .env; set +a` first; the script reads `GROQ_API_KEY` from the shell.
- Python: use `/opt/homebrew/bin/python3.11` (system `python3` is 3.9, too old).
- Backend setup: `cd backend && python3.11 -m venv .venv && .venv/bin/pip install -e ".[dev]"`
- Backend run: `cd backend && .venv/bin/uvicorn app.main:app --reload` → http://localhost:8000/health. It reads the repo-root `.env` itself and creates `backend/dev.db` (SQLite, gitignored) when `DATABASE_URL` is empty.
- A random `JWT_SECRET` was generated into the local `.env` on 2026-11-17.
- Backend checks: `cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/pytest -q`
- Frontend setup/run: `cd frontend && npm install && npm run dev` → http://localhost:5173
- Frontend checks: `cd frontend && npm run lint && npm run build`
- API contract: summary in docs/API.md, interactive at http://localhost:8000/docs; regenerate frontend types with `cd frontend && npm run types`.
- Eval corpus: `python eval/corpus.py check` validates labels; `python eval/corpus.py fetch` re-downloads the gitignored PDFs. Format: `eval/README.md`.
- Spike: needs `brew install tesseract tesseract-lang` and `pip install -e "backend[spike]"`; commands in docs/SPIKE.md §7. Ollama models present: `gemma3:4b`, `qwen2.5:3b`, `llama3.2:3b`.
- Agent prompt smoke test: `set -a; source .env; set +a; python eval/agent_smoke.py` (needs `eval/results/text/` from `python eval/spike.py text`).
- Eval run: not implemented yet (`eval/run_eval.py` is a stub).
- GitHub contributors sidebar may still show Claude from a cached view; the API lists only the owner and no commit carries a co-author line.
- CI: `.github/workflows/lint.yml` runs the backend and frontend checks on push to main and on PRs.
