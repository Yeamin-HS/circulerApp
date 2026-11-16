# ADR-011: SQLAlchemy 2 for database access; SQLite when no `DATABASE_URL` is set
Status: accepted · 2026-11-17
Decision:
1. The backend uses SQLAlchemy 2 (synchronous sessions, typed `Mapped` models) with the
   `psycopg` 3 driver for Postgres.
2. Production and any work that needs vectors uses Neon Postgres through `DATABASE_URL`.
3. When `DATABASE_URL` is empty, the backend uses a local SQLite file (`backend/dev.db`,
   gitignored). Tests use an in-memory SQLite database. This covers accounts and profiles
   (Epic 2). It stops at Story 3.1: pgvector needs Postgres.
4. Tables are created at startup with `create_all` for now. Alembic migrations are added in
   Story 3.1, when the schema starts to change on a database that holds real data.
Why: the owner's machine has no Postgres or Docker and no Neon database yet; auth should
not wait for that. SQLAlchemy keeps the same model code on both databases, is free, and is
the common choice with FastAPI. Sync sessions are simpler than async and FastAPI runs sync
routes in a thread pool, which is enough at demo scale.
Trade-off: SQLite and Postgres differ in details (types, constraint behaviour), so a test
that passes on SQLite is not proof for Postgres. Vector and full-text features cannot be
tested this way at all.
Revisit if: a Neon database exists (then run the test suite against it too), or request
volume makes the sync driver a bottleneck.
