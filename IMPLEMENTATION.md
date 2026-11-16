# IMPLEMENTATION LOG — handoff file between Claude Code and Codex

Read this first. Update it at the end of every session, and before a session runs out of tokens.

## Current state
- Active story: 1.2 Test corpus (drafted, not closed: labels need owner verification and Bijoy circulars are missing).
- Last tool used: Claude Code
- Last updated: 2026-11-16
- Branch: main
- Remote: https://github.com/Yeamin-HS/circulerApp (public)

## Next 3 actions
1. Owner: check each `eval/labels/*.json` against its PDF, fix errors, set `"verified": true`
2. Owner: add at least 2 Bijoy/SutonnyMJ circulars (none found on the 71 gov.bd sites swept) with labels; then Story 1.2 closes
3. Story 1.3: format spike script over `eval/circulars`; record results in docs/SPIKE.md

## Done (newest first)
| Date | Tool | Story | What changed | Files |
|---|---|---|---|---|
| 2026-11-16 | Claude Code | 1.2 | 15 real circulars downloaded from official gov.bd sites (3 digital, 12 scanned, 8 multi-post, 2 English); draft fact-card label per circular; label checker + re-download script; label format documented. Local only, not committed | `eval/labels/*.json`, `eval/corpus.py`, `eval/README.md`, `eval/circulars/*.pdf` (gitignored) |
| 2026-11-16 | Claude Code | 1.1 | Added MIT licence; Story 1.1 closed | `LICENSE` |
| 2026-11-16 | Claude Code | 1.1 | Repo skeleton: backend package folders, FastAPI app with `/health` + test, Vite React-TS app (demo content trimmed), eval folders + stub runner, `.env.example`, `.gitignore`, CI lint workflow; first commit pushed to GitHub | `backend/`, `frontend/`, `eval/`, `.env.example`, `.gitignore`, `.github/workflows/lint.yml` |

## In progress / half-done
- Story 1.2 work is uncommitted: the owner adds, commits and pushes manually.
- All 15 labels are AI drafts (`"verified": false`). They are not ground truth until the owner checks them.
- `eval/run_eval.py` is an intentional stub (exits 1) until Increment 1.

## Known issues / blockers
- Corpus gap: 0 Bijoy circulars (target ≥ 2). `python eval/corpus.py check` reports it as `GAP`.
- Findings for Story 1.3 (see `text_layer` and `notes` in the labels):
  - `c01`: Unicode text layer, but PyMuPDF output is garbled (Nikosh font, vowel signs dropped). "Digital" does not guarantee usable text.
  - `c05`, `c07`: scans carrying a junk Latin-script OCR layer. A "has text layer, no Bangla Unicode" test would misread them as Bijoy; the detector needs a real Bijoy signal (e.g. font names).
  - `c05` page 2 is a different notice (a tender) with its own post table.
- Findings for Story 1.5: age limit and fee often differ per post, and a second apply URL can appear. `FactCard` has one `age_limit`; the labels add `posts[].age_limit` and `apply_mode`.
- pytest prints a Starlette deprecation warning about `httpx` in the test client; harmless for now.

## Decisions made this session
- Owner rule: commit messages carry no `Co-Authored-By` AI trailer (keeps AI tools out of the GitHub contributors list).
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
- Eval corpus: `python eval/corpus.py check` validates labels; `python eval/corpus.py fetch` re-downloads the gitignored PDFs. Format: `eval/README.md`.
- Eval run: not implemented yet (`eval/run_eval.py` is a stub).
- GitHub contributors sidebar may still show Claude from a cached view; the API lists only the owner and no commit carries a co-author line.
- CI: `.github/workflows/lint.yml` runs the backend and frontend checks on push to main and on PRs.
