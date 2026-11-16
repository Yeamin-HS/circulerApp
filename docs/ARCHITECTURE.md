# Architecture Blueprint — Ask the Circular

Status: **draft, awaiting owner approval**. No source code exists yet.

## 1. System overview

```
┌──────────────────────────── Browser (React + TS + Vite, Vercel) ───────────────────────────┐
│ Auth pages · Profile review · Circular upload · Fact card · Eligibility · Chat · Dashboard │
└───────────────┬─────────────────────────────────────────────────────────────────────────────┘
                │ HTTPS, JSON + SSE (Authorization: Bearer <JWT>)
┌───────────────▼──────────────────────── FastAPI (Render free) ──────────────────────────────┐
│ api/        auth · profile · circulars · ask · eligibility · admin                          │
│ ingest/     detect_type → extract_text | ocr | bijoy_convert → normalise → chunk → embed    │
│ extract/    LLM + Pydantic schema → CVProfile, FactCard (validated, evidence-linked)        │
│ rules/      eligibility engine (age, CGPA, degree, experience) — pure Python                │
│ agent/      hand-written loop: route → retrieve → draft → critique → revise/abstain         │
│ llm/        LLMClient interface → OllamaClient (dev) | GroqClient (prod)                    │
│ embed/      multilingual-e5-small on CPU                                                    │
└───────────────┬─────────────────────────────────────────────────────────────────────────────┘
                │ SQL + pgvector
┌───────────────▼──────────── Neon Postgres (free) ───────────┐
│ users · profiles · circulars · posts · chunks(vector 384)   │
│ qa_logs · eval_runs                                          │
└──────────────────────────────────────────────────────────────┘
```

No Node gateway in v1 (ADR-004). Uploaded files are processed in memory or in a temp
directory and are not kept, so no object storage is needed.

## 2. Repository layout

```
circulerApp/
├── CLAUDE.md
├── ROADMAP.md
├── _context/SOP.md
├── _context/decisions/ADR-*.md
├── docs/ARCHITECTURE.md · REQUIREMENTS.md
├── frontend/                 React + TS + Vite
│   └── src/{pages,components,api,hooks,types}
├── backend/
│   ├── app/{api,ingest,extract,rules,agent,llm,embed,db,core}
│   ├── tests/
│   └── pyproject.toml
├── eval/
│   ├── circulars/            test files (gitignored if licence unclear)
│   ├── labels/               hand-written ground truth (JSON per circular)
│   └── run_eval.py           → eval/results/<date>.md
└── .env.example
```

## 3. Data model (Postgres)

| Table | Key columns | Notes |
|---|---|---|
| `users` | id, email (unique), password_hash, role (`seeker`/`admin`), consent_at, created_at | argon2 hash |
| `profiles` | user_id (PK/FK), data JSONB (`CVProfile`), confirmed_at | only confirmed profiles are used |
| `circulars` | id, owner_id (FK, NULL = shared), title, org, source_type (`digital`/`scanned`/`bijoy`), fact_card JSONB, deadline DATE, created_at | shared circulars are v1.1 |
| `posts` | id, circular_id, title, vacancies, grade, requirements JSONB | one row per post |
| `chunks` | id, circular_id, post_id NULL, page, kind (`text`/`table_row`), text, embedding VECTOR(384) | HNSW index on embedding |
| `qa_logs` | id, user_id, circular_id, question_hash, route, n_llm_calls, abstained, latency_ms, created_at | no question text stored for privacy; cache lives in memory |
| `eval_runs` | id, run_at, config JSONB, metrics JSONB | admin only |

All seeker queries filter on `owner_id = current_user OR owner_id IS NULL`.
Account deletion cascades through every table.

## 4. Core schemas (Pydantic, abbreviated)

```python
class Degree(BaseModel):
    level: Literal["SSC","HSC","Diploma","Bachelor","Masters","PhD"]
    subject: str | None
    institution: str | None
    result: float | None            # CGPA or GPA
    result_scale: float | None      # 4.0 / 5.0
    division: str | None            # older "1st division" style results
    passing_year: int | None

class CVProfile(BaseModel):
    full_name: str
    date_of_birth: date | None
    degrees: list[Degree]
    experience: list[Experience]    # title, org, start, end
    skills: list[str]
    certifications: list[str]

class Evidence(BaseModel):
    chunk_id: int
    quote: str                      # exact substring of the chunk

class FieldValue[T](BaseModel):
    value: T | None                 # None → "Not stated"
    evidence: list[Evidence]

class PostReq(BaseModel):
    title: FieldValue[str]
    vacancies: FieldValue[int]
    min_degree: FieldValue[str]
    subjects: FieldValue[list[str]]
    min_result: FieldValue[str]
    experience_years: FieldValue[float]

class FactCard(BaseModel):
    organisation: FieldValue[str]
    posts: list[PostReq]
    deadline: FieldValue[date]
    age_limit: FieldValue[int]
    age_as_of: FieldValue[date]
    fee: FieldValue[str]
    how_to_apply: FieldValue[str]
    apply_link: FieldValue[str]
```

Validation rule: an `Evidence.quote` must be an exact substring of its chunk, otherwise the
field is reset to "Not stated". This mechanically blocks invented values. `apply_link` must
also appear verbatim in the document text.

## 5. Pipelines

### 5.1 Circular ingestion
1. **Validate**: MIME and magic bytes, size ≤ 10 MB, page count ≤ 20.
2. **Detect type**:
   - text layer that is clean English, or Bangla Unicode with intact vowel signs → `digital`
   - more than half of the text-layer characters set in a Bijoy font (`*MJ`, Sutonny) → `bijoy`
   - no text layer, an image, or a text layer that is garbled or junk → `scanned`
   (rules and thresholds measured in docs/SPIKE.md §2)
3. **Get text**: PyMuPDF for a usable text layer · Tesseract `ben+eng` at 200 dpi for
   everything else: scans, garbled or junk text layers, and Bijoy (ADR-005, ADR-006).
4. **Normalise**: Bangla→ASCII digits, Bangla month names → ISO dates, whitespace cleanup.
5. **Chunk**: by heading or paragraph, about 300–500 tokens; **each table row is its own
   chunk** tagged with its post; keep the page number.
6. **Embed** with the `passage:` prefix (e5 convention) and store.
7. **Extract** the FactCard in a single LLM call, validate evidence, then store posts.

### 5.2 CV → profile
PyMuPDF / python-docx → text → one LLM call to `CVProfile` → review screen → confirm →
delete the file. A hidden-text check flags white or tiny-font text before extraction.

### 5.3 Eligibility engine (pure Python)
For each post: compare age as of `age_as_of`, degree level ordering, result against
`min_result` (handles CGPA scale and divisions), and experience years. Each check returns
`pass` / `fail` / `unknown` with the evidence passed through. **Subject matching** is the
only LLM step: "Is 'CSE' within {'Computer Science', 'ICT', 'related subject'}?" →
yes / no / unclear plus a quote. Overall verdict: any `fail` → not eligible; any `unknown`
→ unclear; otherwise eligible.

## 6. Agent loop (hand-written)

This is the overview. The detailed design (states, budgets, data shapes, prompts and their
smoke test) is in docs/AGENT.md.

```
question
  │
  ▼
ROUTE (1 LLM call, JSON) → fact_lookup | eligibility | summary | out_of_scope
  │                           out_of_scope → polite refusal, end
  ▼
GATHER (tools, no LLM):
  retrieve(query, circular_id, k=6)      hybrid: pgvector cosine + Postgres full-text, RRF
  get_profile(user_id)                   eligibility route only
  check_eligibility(post_id)             eligibility route only (section 5.3)
  ▼
DRAFT (1 LLM call, streamed): answer with [c:<chunk_id>] citations, using only gathered context
  ▼
CRITIQUE (1 LLM call, JSON): for each sentence → supported / unsupported + reason
  ├─ all supported → return
  ├─ unsupported and rounds < 2 → REVISE (remove or fix the unsupported claims) → CRITIQUE
  └─ still failing → ABSTAIN: "This isn't clearly stated in the circular." + best citations
```

- Budget: normally 3 calls (route, draft, critique); hard cap 5 calls and 2 revisions,
  whichever comes first (docs/AGENT.md §4). Each role uses its own Groq model with a token
  cap per call (ADR-009).
- Streaming: the draft streams to the UI, which marks it "verifying…". If the critique
  rejects it, the UI replaces the text with the revised answer.
- Cache: in-memory LRU keyed on (circular_id, normalised question, profile_version).
- Injection defence: every source is wrapped in `<source id="...">` tags, and each prompt
  says content inside them is data only.

## 7. API contracts (v1)

| Method & path | Auth | Purpose |
|---|---|---|
| `POST /auth/register` · `POST /auth/login` | — | returns JWT (60 min) |
| `DELETE /me` | seeker | delete account and all data |
| `POST /me/cv` | seeker | upload CV → draft `CVProfile` (not saved) |
| `PUT /me/profile` | seeker | save the confirmed profile |
| `GET /me/profile` | seeker | — |
| `POST /circulars` | seeker | upload → ingest → `{id, fact_card}` |
| `GET /circulars` | seeker | own (+ shared, v1.1) list with deadline and verdict |
| `GET /circulars/{id}` | seeker | fact card + posts |
| `GET /circulars/{id}/eligibility` | seeker | per-post verdicts with evidence |
| `POST /circulars/{id}/ask` | seeker | SSE stream: `token`, `citation`, `critique`, `final` events |
| `GET /chunks/{id}` | seeker | source text for citation highlighting |
| `POST /admin/eval` · `GET /admin/metrics` | admin | v1.1 |
| `GET /health` | — | warm-up ping |

## 8. Deployment ($0)

| Part | Service | Watch out for |
|---|---|---|
| Frontend | Vercel Hobby | — |
| Backend | Render free web service | sleeps when idle (cold start); RAM ~512 MB, so measure it in Story 1.3 |
| DB | Neon free (pgvector) | storage cap; scale-to-zero adds a short wake delay |
| LLM | Groq free tier (prod), Ollama (dev) | daily request cap; check limits before launch |
| CI | GitHub Actions (public repo) | lint, tests, small eval subset |

Free-tier limits change; re-check every quota before deploying.

## 9. Evaluation plan
- **Set**: 12–15 real circulars (≥ 3 scanned, ≥ 2 Bijoy, ≥ 3 multi-post) with hand-written
  fact cards; 3 synthetic profiles × all posts → eligibility labels; 40 Q&A pairs including
  10 that are deliberately unanswerable.
- **Metrics**: field accuracy by source type; eligibility accuracy; citation precision (does
  the cited chunk support the claim); abstention correctness on unanswerable questions;
  hallucination count; latency p50/p95; LLM calls per question.
- **Ablations for the README**: dense vs hybrid retrieval; with vs without critique;
  Tesseract vs alternative OCR.

## 10. Open items (resolve during Phase 1)
1. Repo location: new folder on the owner's Mac vs cloud workspace + GitHub `Yeamin-HS`.
2. Bijoy→Unicode converter: resolved for v1 by ADR-006 (Bijoy goes through OCR; revisit
   with real Bijoy circulars).
3. OCR engine: resolved by ADR-005 (Tesseract `ben+eng`, 200 dpi).
4. Which Groq-hosted model handles Bangla best: resolved by ADR-007 (`qwen/qwen3.8-27b`,
   fallback `openai/gpt-oss-120b`).
5. Does embedding + OCR fit Render's free RAM? OCR does (ADR-008); the embedding model is
   not measured yet.
6. JWT storage: an in-memory token means signing in again after refresh. localStorage carries
   XSS risk (mitigated with a strict CSP). Cross-site cookies (Vercel ↔ Render) can be blocked
   by Safari. Decide in Story 2.1.
