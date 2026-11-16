# ADR-002: Hand-written agent loop, no framework
Status: accepted · 2026-11-14
Decision: route → gather → draft → critique → revise/abstain is written as plain Python with
explicit state, a call budget (≤ 5 LLM calls) and JSON outputs validated by Pydantic.
Why: easier to debug and explain in interviews; no dependency churn; the call budget is
needed to stay within the free tier.
Trade-off: no built-in tracing; we log route, call count, abstain flag and latency ourselves.
