# Ask the Circular — AI assistant instructions

This project is built alternately with Claude Code and Codex. `AGENTS.md` holds the same
rules for Codex. Read `IMPLEMENTATION.md` first (current state and handoff), then
`_context/SOP.md`. Update `IMPLEMENTATION.md` at the end of every session and before
running out of tokens.

Read `_context/SOP.md` before doing anything in this repo. It holds the project intent,
hard rules, and current phase. Architecture lives in `docs/ARCHITECTURE.md`, requirements
in `docs/REQUIREMENTS.md`, plan in `ROADMAP.md`, decisions in `_context/decisions/`.

Working rules:
- Do not add paid services, paid API keys, or paid hosting tiers.
- Do not add LangChain/LangGraph or similar agent frameworks (see ADR-002).
- Deliver code edits as changed chunks, not full-file rewrites.
- Stay scoped to the current story in ROADMAP.md; propose extras separately.
- Any new architectural choice → write an ADR in `_context/decisions/` first.
- Update the "Current phase / status" block in `_context/SOP.md` at the end of each session.
