# ADR-010: API contract v1 is frozen as an OpenAPI snapshot
Status: accepted · 2026-11-17
Decision:
1. The v1 contract is the Pydantic models in `backend/app/core/schemas.py` and the routes in
   `backend/app/api/`. Until a story implements a route, it is a stub that returns 501.
2. `docs/openapi.json` is the frozen snapshot. A test fails when the app's OpenAPI differs
   from it. Changing the contract means regenerating the snapshot on purpose
   (`UPDATE_OPENAPI=1 pytest tests/test_contract.py`) and noting why in IMPLEMENTATION.md.
3. Frontend types in `frontend/src/types/api.d.ts` are generated from the snapshot, never
   written by hand.
4. Changes to the draft schemas in ARCHITECTURE §4 and §7, each from a finding in Stories
   1.2–1.4:
   - `PostReq` gains `grade` (FR-10) and `age_limit`; `FactCard` gains `apply_mode`. Age limit
     differed per post in the test circulars.
   - Degree levels gain `Class 8` and `JSC`; 7 of 15 test circulars have such posts.
   - Two endpoints are added: `GET /me` (the UI needs role, consent and profile state) and
     `POST /me/consent` (consent must exist before a CV is uploaded, FR-02).
   - The ask stream gains a `status` event (busy / retry, ADR-009). `citation` events carry
     source ids of all three kinds (`c:N`, `p`, `e:N`).
   - Every error has one shape: `{"error": {"code", "message"}}` with a fixed code list.
5. `POST /admin/eval` and `GET /admin/metrics` are v1.1 and not part of the frozen contract.
Why: the frontend and backend are built in alternating sessions by two AI tools; a snapshot
test is the cheapest way to stop either side drifting. Stubs make the contract visible in
`/docs` from day one.
Trade-off: any schema fix now costs a snapshot update and a types regeneration.
Revisit if: the snapshot test blocks work more often than it catches real drift.
