# ADR-004: No Node gateway in v1
Status: accepted · 2026-11-14
Decision: The React frontend calls FastAPI directly. Auth, DB access and the ML work all live
in FastAPI.
Why: a Node layer adds about a day of plumbing and a second cold-starting service with no AI
value for this scope.
Revisit if: a NestJS gateway becomes a deliberate learning or portfolio goal.
