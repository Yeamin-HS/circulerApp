# Requirements

Priority: **M** = must (v1), **S** = should (v1.1), **C** = could (later).
Targets marked *(proposed)* are confirmed or revised after the baseline evaluation run.

## Functional requirements

### Accounts and profile
| ID | Requirement | Pri |
|---|---|---|
| FR-01 | Sign up / sign in with email and password; roles `seeker` and `admin` | M |
| FR-02 | Consent screen before any profile data is stored | M |
| FR-03 | Upload CV (PDF/DOCX, ≤ 5 MB) → extract a structured profile | M |
| FR-04 | Review-and-edit screen; only the **confirmed** profile is used anywhere | M |
| FR-05 | CV file deleted after confirmation; extracted profile kept | M |
| FR-06 | One-click "delete my account and all data" | M |

### Circulars
| ID | Requirement | Pri |
|---|---|---|
| FR-07 | Upload circular (PDF/JPG/PNG, ≤ 10 MB) | M |
| FR-08 | Detect type: digital text / scanned / Bijoy-encoded, and route to extract / OCR / convert | M |
| FR-09 | Normalise Bangla digits and dates (৩০/১১/২০২৬ → 2026-11-30) | M |
| FR-10 | Fact card: organisation, posts (title, vacancies, grade, qualification, experience), deadline, age limit + "as of" date, fee, how to apply, apply link | M |
| FR-11 | Missing fields show "Not stated"; every filled field links to its source passage | M |
| FR-12 | Per-post eligibility verdict (eligible / not eligible / unclear) with reasons and citations | M |
| FR-13 | Gap list per post (e.g. "needs 2 years' experience; you have 0") | M |

### Q&A agent
| ID | Requirement | Pri |
|---|---|---|
| FR-14 | Ask in Bangla or English; answer language follows the question; answers stream | M |
| FR-15 | Answers cite passages; clicking a citation highlights the source text | M |
| FR-16 | Agent can use the profile ("Am I eligible for post 3?") | M |
| FR-17 | Self-critique: verify each claim against cited text; revise ≤ 2 times or abstain | M |
| FR-18 | "Show reasoning" panel: route, retrieved chunks, critique result | S |

### Dashboard and admin
| ID | Requirement | Pri |
|---|---|---|
| FR-19 | "My circulars" list sorted by deadline, with eligibility badge | S |
| FR-20 | Admin publishes verified shared circulars visible to all seekers | S |
| FR-21 | Admin views usage/error metrics and triggers an evaluation run | S |
| FR-22 | Export fact card; add deadline to calendar (.ics) | C |

## Non-functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Cost | $0 to build, run and deploy |
| NFR-02 | Grounding | 0 unsupported claims on the evaluation set; every claim cited or abstained |
| NFR-03 | Extraction accuracy | ≥ 85% field accuracy on digital circulars, ≥ 70% on scanned *(proposed)* |
| NFR-04 | Eligibility accuracy | ≥ 90% correct per-post verdicts on the labelled set *(proposed)* |
| NFR-05 | Latency | First answer token < 3 s (warm); fact card < 15 s digital, < 40 s scanned *(proposed)* |
| NFR-06 | Free-tier fit | ≤ 4 LLM calls per question; identical questions cached; backend fits ~512 MB RAM |
| NFR-07 | Cold start | UI pings backend on load and shows a "waking up server" state |
| NFR-08 | Privacy | Consent, CV file deletion, real data deletion, no profile data in logs (PDPO 2025) |
| NFR-09 | Security | argon2 password hashing; JWT expiry; per-user row filtering on every query; file type/size checks; IP rate limits; document text treated as data |
| NFR-10 | Language | Bangla and English input and output |
| NFR-11 | Usability | Mobile-first layout; light and dark mode |
| NFR-12 | Maintainability | Typed Pydantic schemas; swappable `LLMClient`; ADRs for decisions |
| NFR-13 | Evaluability | One command runs the labelled set and writes a metrics table for the README |
