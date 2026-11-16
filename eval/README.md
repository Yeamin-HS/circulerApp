# Evaluation corpus

Real Bangladeshi job circulars and their ground-truth fact cards (Story 1.2).

- `circulars/` holds the PDF files. They are **gitignored** (licence unclear). Restore them
  with `python eval/corpus.py fetch`, which downloads each file from its official source
  URL and checks its SHA-256.
- `labels/<id>.json` holds one ground-truth label per circular.
- `python eval/corpus.py check` validates every label and prints corpus coverage.
- `eval/spike.py` is the Story 1.3 format spike; its results are in `docs/SPIKE.md`.

## Status

All 15 labels are **drafts** (`"verified": false`, `"labelled_by": "claude-draft"`). They
were read from page images by an AI assistant, not by the owner. Before a label counts as
ground truth, the owner must compare it with the PDF, fix anything wrong, and set
`"verified": true`. Do not report accuracy numbers against unverified labels.

Known gap: the corpus has **no Bijoy / SutonnyMJ circular** yet (target: at least 2).

## Label format

Top level:

| Field | Meaning |
|---|---|
| `id`, `file` | `file` is always `<id>.pdf` inside `circulars/` |
| `source_url`, `sha256` | official download URL and the hash of the downloaded file |
| `source_type` | `digital`, `scanned` or `bijoy` (ARCHITECTURE §5.1) |
| `text_layer` | what PyMuPDF finds: `unicode` (usable), `garbled_unicode` (Bangla with broken vowel signs), `junk_ocr` (Latin gibberish over a scan), `none` |
| `language` | `bn`, `en` or `mixed` |
| `multi_post` | true when the circular has more than one post |
| `verified` | true only after the owner has checked the label against the PDF |
| `notes` | traps and caveats worth knowing when a result looks wrong |
| `fact_card` | the ground truth, below |

`fact_card` follows `FactCard` in ARCHITECTURE §4, with plain values instead of
`FieldValue` wrappers. `null` always means "not stated in the circular".

| Field | Type | Notes |
|---|---|---|
| `organisation` | string | as printed |
| `posts[].title` | string | as printed, without grade or pay scale |
| `posts[].vacancies` | int | |
| `posts[].min_degree` | `Class 8`, `JSC`, `SSC`, `HSC`, `Diploma`, `Bachelor`, `Masters`, `PhD` | lowest level that qualifies |
| `posts[].subjects` | list of strings | only when the circular restricts the subject |
| `posts[].min_result` | string | e.g. `2nd class` |
| `posts[].experience_years` | number | only when required, not when merely preferred |
| `posts[].age_limit` | int | set only where posts differ; not in the `FactCard` schema yet |
| `deadline` | ISO date | last date to apply |
| `age_limit` | int | upper limit for general candidates; null when it differs per post |
| `age_as_of` | ISO date | the date on which age is counted |
| `fee` | string | amounts in taka, with the posts they apply to |
| `apply_mode` | `online`, `post_or_in_person`, `email_or_in_person` | not in the `FactCard` schema yet |
| `how_to_apply` | string | short English summary |
| `apply_link` | string | URL exactly as printed |
