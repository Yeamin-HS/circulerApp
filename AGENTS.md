# Ask the Circular — instructions for AI coding agents (Codex and others)

This file mirrors CLAUDE.md so that Codex and Claude Code follow the same rules.

Start of every session:
1. Read `IMPLEMENTATION.md` (current state and next actions).
2. Read `_context/SOP.md` (intent, hard rules, stack).
3. Work only on the active story in `ROADMAP.md`.

End of every session, or when about to run out of tokens:
- Update `IMPLEMENTATION.md`: current state, done rows, half-done work, blockers, next 3 actions.
- Commit with a message that names the story id (e.g. `feat(3.1): chunk table rows`).

Rules:
- $0 only: no paid services, keys, or hosting tiers.
- No LangChain/LangGraph or similar agent frameworks (ADR-002).
- Deliver code edits as changed chunks, not full-file rewrites.
- New architectural choice → write an ADR in `_context/decisions/` first.
- Architecture: docs/ARCHITECTURE.md · Requirements: docs/REQUIREMENTS.md
