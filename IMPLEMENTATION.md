# IMPLEMENTATION LOG — handoff file between Claude Code and Codex

Read this first. Update it at the end of every session, and before a session runs out of tokens.

## Current state
- Active story: 1.2 Test corpus (not started). Story 1.1 is done except for the licence file.
- Last tool used: Claude Code
- Last updated: 2026-11-16
- Branch: main
- Remote: https://github.com/Yeamin-HS/circulerApp (public)

## Next 3 actions
1. Owner picks a licence (ROADMAP 1.1 lists one); add `LICENSE` to close Story 1.1
2. Story 1.2: put test circulars in eval/circulars and write labels in eval/labels
3. Story 1.3: format spike script; record results in docs/SPIKE.md

## Done (newest first)
| Date | Tool | Story | What changed | Files |
|---|---|---|---|---|
| 2026-11-16 | Claude Code | 1.1 | Repo skeleton: backend package folders, FastAPI app with `/health` + test, Vite React-TS app (demo content trimmed), eval folders + stub runner, `.env.example`, `.gitignore`, CI lint workflow; first commit pushed to GitHub | `backend/`, `frontend/`, `eval/`, `.env.example`, `.gitignore`, `.github/workflows/lint.yml` |

## In progress / half-done
- Nothing half-written. `eval/run_eval.py` is an intentional stub (exits 1) until Increment 1.

## Known issues / blockers
- No `LICENSE` yet: waiting for the owner's choice.
- pytest prints a Starlette deprecation warning about `httpx` in the test client; harmless for now.

## Decisions made this session
- Minor, no ADR: plain `venv` + `pip` with setuptools (no `uv`); `ruff` for Python lint/format.
- Minor, no ADR: the current Vite `react-ts` template ships `oxlint` instead of ESLint; kept as is.
- `eval/circulars/*` and `eval/results/*` are gitignored (ARCHITECTURE §2: licence unclear).

## Environment notes
- Required env vars: see .env.example
- Python: use `/opt/homebrew/bin/python3.11` (system `python3` is 3.9, too old).
- Backend setup: `cd backend && python3.11 -m venv .venv && .venv/bin/pip install -e ".[dev]"`
- Backend run: `cd backend && .venv/bin/uvicorn app.main:app --reload` → http://localhost:8000/health
- Backend checks: `cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/pytest -q`
- Frontend setup/run: `cd frontend && npm install && npm run dev` → http://localhost:5173
- Frontend checks: `cd frontend && npm run lint && npm run build`
- Eval: not implemented yet (`eval/run_eval.py` is a stub).
- CI: `.github/workflows/lint.yml` runs the backend and frontend checks on push to main and on PRs.
