# ADR-007: `qwen/qwen3.8-27b` on Groq for production, `gemma3:4b` on Ollama for development
Status: accepted · 2026-11-17 (dev part 2026-11-16)
Decision:
1. Production LLM: `qwen/qwen3.8-27b` on Groq's free tier. Fallback if it is withdrawn or
   rate-limited: `openai/gpt-oss-120b`.
2. Local development default: `gemma3:4b` on Ollama. It is for wiring and debugging only;
   accuracy targets (NFR-03) are measured on the production model.
3. The model name is configuration, not code, so it can change without a release.
Why (docs/SPIKE.md §5): fact-card extraction on the 15 test circulars, 9 fields each.

| Model | Fields right | Scanned | Digital | Valid JSON | Median time |
|---|---|---|---|---|---|
| `qwen/qwen3.8-27b` (Groq) | 91% | 92% | 90% | 15/15 | 1.0 s |
| `openai/gpt-oss-120b` (Groq) | 87% | 85% | 94% | 15/15 | 2.4 s |
| `openai/gpt-oss-20b` (Groq) | 83% | 81% | 90% | 14/15 | 2.0 s |
| `gemma3:4b` (Ollama) | 60% | 57% | 73% | 15/15 | 10 s |

These were the only three chat models the free key could use. The top two both clear the
proposed targets (85% digital, 70% scanned); `qwen/qwen3.8-27b` is ahead on scanned files,
which are most of real circulars, and is the fastest. The 4-point gap between the top two is
within what one run on 15 files can show, hence the named fallback. The local 3 B models
scored 22–25%, and a more detailed prompt did not help `gemma3:4b` (55%).
Consequences for Story 3.2:
- Groq's free tier allows about 8,000 tokens per minute per model. One long circular uses
  most of that, and `gpt-oss-20b` rejected one file as too large. Extraction must send the
  circular in parts (header facts, then the post table) and retry on HTTP 429.
- Cap output tokens on every call (`qwen2.5:3b` ran away in JSON mode).
- Validate `apply_link` against the document text: models returned the organisation's home
  page or an OCR-damaged URL in 3–7 of 15 files.
Caveats: one run, 15 files, draft labels not yet verified by the owner. Free-tier models
and limits change; re-check before launch (ARCHITECTURE §8).
Revisit if: the chosen model leaves the free tier, or verified labels change the ranking.
