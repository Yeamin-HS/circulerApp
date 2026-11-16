# ADR-009: One model per agent role, with a token budget per call
Status: accepted · 2026-11-17
Context: Groq's free tier gives each model its own allowance: 8,000 tokens per minute and
1,000 requests per day (read from the API's rate-limit headers on 2026-11-17). The allowance
is per account, so every user of the deployed app shares it. A question that makes three
calls of about 3,000 tokens on one model would exceed that model's minute on its own.
Decision:
1. Each agent role uses a different Groq model, so each role draws on its own allowance:
   route → `openai/gpt-oss-20b`; draft and revise → `qwen/qwen3.8-27b`;
   critique → `openai/gpt-oss-120b`. In development all roles use the one Ollama model.
2. Every call has a hard input and output token cap (table in docs/AGENT.md §5). Retrieved
   context is cut to fit; the agent never sends a whole circular.
3. Python checks run before any LLM critique: citation ids must exist in the gathered
   sources, and every sentence must carry a citation. A draft that fails gets one revision
   without spending a critique call.
4. Questions that map to a fact-card field with stored evidence are answered from the fact
   card by template, with its citation, and no draft call. The critique still runs.
5. On HTTP 429 the agent does not wait silently: it returns a "busy, retry in N seconds"
   event to the UI. It falls back to the other model for the same role once.
Why: it keeps the hand-written loop (ADR-002) inside the free tier (hard rule 1) without
dropping the critique step (hard rule 4). A critic that is a different model from the
drafter is also less likely to repeat the drafter's mistake.
Trade-off: three model names to keep working instead of one; behaviour in development (one
small model) differs from production.
Revisit if: Groq changes the free limits or removes a model; or measured token use per
question (docs/AGENT.md §7) grows past the caps.
