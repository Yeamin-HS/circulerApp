# ADR-007: `gemma3:4b` for local development; production model still to be chosen
Status: accepted for dev; production part open · 2026-11-16
Decision:
1. The default Ollama model for local development is `gemma3:4b`.
2. No 3–4 B local model is good enough to judge the product by. Accuracy targets (NFR-03)
   are measured only on the production model.
3. The production (Groq) model is **not chosen yet**. It will be picked by running
   `python eval/spike.py llm groq:<model-a> groq:<model-b>` on the same 15 circulars and
   taking the higher field accuracy, with valid-JSON rate as the tie-breaker.
Why (docs/SPIKE.md §4): on fact-card extraction from the 15 test circulars `gemma3:4b`
got 60% of fields right and always returned valid JSON. `qwen2.5:3b` got 25% (valid JSON
11/15, and it hung once in an endless-whitespace loop until output was capped).
`llama3.2:3b` got 22% (13/15). A more detailed prompt with Bangla degree hints and a larger
context did not help `gemma3:4b` (55%), so the limit is model capacity, not prompt wording.
Consequences for Story 3.2: do not rely on one big extraction call. Cap output tokens on
every call. Take dates and URLs from the text with Python and let the LLM choose among
them. Extract the post table separately from the header facts.
Blocked on: a free `GROQ_API_KEY` from the owner. The list of free Groq models changes, so
pick the two candidates from Groq's current model page at that time.
Caveat: scores are against draft labels the owner has not verified yet.
