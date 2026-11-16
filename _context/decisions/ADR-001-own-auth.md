# ADR-001: Own auth in FastAPI
Status: accepted (provisional, owner to confirm) · 2026-11-14
Context: Login and roles are needed; options were Supabase Auth or a hand-built one.
Decision: Email and password, argon2 hashing, JWT bearer (60 min), role claim, written in
FastAPI. No Google sign-in in v1.
Why: fits the owner's build-from-scratch preference; no extra service; shows backend skill.
Trade-off: the owner carries security responsibility; there is no password reset in v1.
Revisit if: auth takes more than half a day or a password-reset flow is needed.
