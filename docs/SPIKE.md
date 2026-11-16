# Format spike — results (Story 1.3)

Run on 2026-11-16 with `eval/spike.py` over the 15 test circulars in `eval/circulars`
(43 pages: 12 scanned, 3 digital, 0 Bijoy). Machine: Apple Silicon Mac, 16 GB.
Raw outputs are in `eval/results/` (gitignored).

**Read this first:** every score below is measured against draft labels that the owner has
not verified yet. Treat the numbers as indicative, not final.

## 1. Summary

| Question | Answer | Decision |
|---|---|---|
| Can we tell digital, scanned and unusable text layers apart? | Yes: 15 of 15 files classified correctly | rule set in `detect()`, §2 |
| Is Tesseract good enough for scanned Bangla circulars? | Yes: 98% of labelled facts recovered (fuzzy), 85% exact | ADR-005 |
| Which OCR settings? | 200 dpi, default segmentation, no OpenCV step | ADR-005 |
| How do we handle Bijoy? | Through OCR for now; the PyPI converter is not accurate enough | ADR-006 (provisional) |
| Which LLM? | `gemma3:4b` for dev (60% of fields); production model not chosen | ADR-007 (part open) |
| Does it fit in 512 MB? | Server + one OCR page ≈ 230 MB; embedding model not measured | ADR-008 (part open) |

Still open after this spike: the production LLM (needs a Groq key), the embedding model's
memory (needs the model files), Bijoy on real circulars (needs samples), and OCR speed on
Render's CPU.

## 2. Type detection

`detect()` reads the PDF text layer with PyMuPDF and returns a source type and a text-layer
quality. Result: **15 of 15** match the labels.

| Text layer | Rule | Route | Files |
|---|---|---|---|
| none | under 50 characters per page | OCR | 10 |
| unicode | ≥ 30% Bangla letters with intact vowel signs, or clean English words | use text layer | 2 (c02, c03) |
| garbled_unicode | Bangla letters, but > 3% of words start with a dependent vowel sign | OCR | 1 (c01) |
| junk_ocr | text present, but neither Bangla nor clean English | OCR | 2 (c05, c07) |
| bijoy | > 50% of characters are set in a Bijoy font (`*MJ`, Sutonny) | OCR (ADR-006) | 0 |

Three traps the corpus exposed:
- **A text layer is not proof of a digital file.** Two scans carry a junk Latin-script OCR
  layer, and the one "digital" Bangla PDF extracts with its vowel signs dropped. Only 2 of
  15 files have a text layer worth using, and both are English.
- **Bijoy must be judged by character share, not by font list.** A real gazette lists
  SutonnyMJ among its fonts but uses it for 4% of the text; the rest is a Nikosh font with
  no usable Unicode mapping.
- **One PDF can hold two notices.** c05 page 2 is a tender with its own post table.

## 3. Text extraction and OCR

"Recall" is the share of labelled facts (organisation, every post title, deadline, age
reference date, apply link: 110 probes) found in the extracted text after normalising digits
and spacing. Exact = the whole string is present; fuzzy = share of its character trigrams
present.

| Method | Scanned (12): fuzzy | Scanned: exact | All 15: fuzzy | CPU s/page | Peak RSS |
|---|---|---|---|---|---|
| PyMuPDF text layer | 0.01 | 0.01 | 0.18 | 0.0 | — |
| **Tesseract 200 dpi** | **0.98** | **0.85** | **0.98** | **2.2** | **118 MB** |
| Tesseract 300 dpi | 0.98 | 0.86 | 0.98 | 2.8 | 188 MB |
| Tesseract 300 dpi + OpenCV deskew/binarise | 0.96 | 0.84 | 0.95 | 2.5 | 117 MB |
| Tesseract 300 dpi, `--psm 6` | 0.95 | 0.83 | 0.95 | 2.8 | 193 MB |

All Tesseract runs use `-l ben+eng`, the stock `tessdata_fast` models and one thread.

Fuzzy recall per file:

| File | Pages | Detected | PyMuPDF | Tess 200 | Tess 300 | 300 + OpenCV | 300 psm 6 |
|---|---|---|---|---|---|---|---|
| c01 | 2 | digital / garbled_unicode | 0.64 | 0.94 | 0.94 | 0.78 | 0.94 |
| c02 | 2 | digital / unicode | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| c03 | 1 | digital / unicode | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| c04 | 1 | scanned / none | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| c05 | 2 | scanned / junk_ocr | 0.00 | 0.94 | 0.92 | 0.92 | 0.78 |
| c06 | 1 | scanned / none | 0.00 | 0.94 | 0.89 | 0.73 | 0.71 |
| c07 | 1 | scanned / junk_ocr | 0.12 | 0.88 | 1.00 | 1.00 | 0.93 |
| c08 | 4 | scanned / none | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| c09 | 4 | scanned / none | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| c10 | 4 | scanned / none | 0.00 | 1.00 | 1.00 | 0.91 | 1.00 |
| c11 | 5 | scanned / none | 0.00 | 0.97 | 0.97 | 0.96 | 0.97 |
| c12 | 4 | scanned / none | 0.00 | 1.00 | 0.99 | 1.00 | 0.99 |
| c13 | 4 | scanned / none | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| c14 | 4 | scanned / none | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| c15 | 4 | scanned / none | 0.00 | 0.99 | 0.99 | 0.94 | 0.99 |

Notes:
- 200 dpi matches 300 dpi on average and is cheaper. c07 is the one file where 300 dpi is
  clearly better (0.88 → 1.00); a retry at 300 dpi when extraction looks poor is an option.
- OpenCV preprocessing and `--psm 6` do not help on this corpus.
- For the garbled digital file (c01), OCR of the rendered page beats its own text layer
  (0.94 vs 0.64).
- Exact recall is lower than fuzzy mostly because of small OCR slips inside long post
  titles (a dropped hasanta or vowel sign). The fact-card step therefore needs fuzzy
  matching when it checks evidence quotes against OCR text.
- Not tested: `tessdata_best` models, other OCR engines, and speed on Render's shared CPU.

## 4. Bijoy conversion

The corpus has no Bijoy circular: two sweeps of 71 government sites found none. The only
real Bijoy text found was 1,306 characters of page headers in a 2019 gazette.

| Approach | Result on that sample |
|---|---|
| `bijoy2unicode` 0.1.1 (PyPI) | Mostly right, but 3 kinds of error: রেজিস্টাডর্ (for রেজিস্টার্ড), কতৃর্পÿ (for কর্তৃপক্ষ), ফেব্রম্নয়ারি (for ফেব্রুয়ারি) |
| Tesseract on the rendered page | Body text read correctly, including ফেব্রুয়ারি; the decorative masthead was missed |

Decision (ADR-006, provisional): route Bijoy files through OCR in v1. Revisit with real
Bijoy circulars.

## 5. LLM fact-card extraction

Each model got the best available text (PyMuPDF for c02/c03, Tesseract 200 dpi for the
rest) and one request for a JSON fact card. Nine fields were scored against the label:
organisation, deadline, age limit, age reference date, apply link, post count, post titles,
vacancies and minimum degree. Only local Ollama models were tested; no Groq key was
available.

| Model | Valid JSON | All 15 | Scanned 12 | Digital 3 | Median time | Slowest |
|---|---|---|---|---|---|---|
| **gemma3:4b** | 15/15 | **0.60** | 0.57 | 0.73 | 10 s | 26 s |
| qwen2.5:3b | 11/15 | 0.25 | 0.17 | 0.59 | 12 s | 24 s |
| llama3.2:3b | 13/15 | 0.22 | 0.14 | 0.56 | 9 s | 22 s |
| gemma3:4b, detailed prompt (v2) | 15/15 | 0.55 | 0.50 | 0.74 | 10 s | 29 s |

Accuracy per field (all 15 files):

| Field | gemma3:4b | qwen2.5:3b | llama3.2:3b | gemma3:4b v2 |
|---|---|---|---|---|
| organisation | 1.00 | 0.33 | 0.33 | 1.00 |
| post titles | 0.81 | 0.31 | 0.29 | 0.81 |
| age limit | 0.80 | 0.40 | 0.33 | 0.53 |
| post count | 0.73 | 0.33 | 0.33 | 0.60 |
| vacancies | 0.68 | 0.09 | 0.20 | 0.75 |
| deadline | 0.40 | 0.27 | 0.07 | 0.27 |
| apply link | 0.40 | 0.20 | 0.13 | 0.40 |
| age reference date | 0.33 | 0.20 | 0.13 | 0.33 |
| minimum degree | 0.27 | 0.15 | 0.16 | 0.25 |

What this shows:
- No local model meets the proposed targets (NFR-03: 85% digital, 70% scanned). The best
  is 73% and 57%.
- `gemma3:4b` finds names (organisation, post titles) but is weak on dates and on mapping
  qualifications to a degree level; it often writes the pay grade as the degree
  ("Class 14").
- The v2 prompt added Bangla degree hints, a deadline definition, ASCII digits and a
  larger context. It did not help. Prompt wording is not the bottleneck at this model size.
- `qwen2.5:3b` once produced output without end in JSON mode; every call needs an output
  token cap.
- Median 10 s per circular on a Mac GPU is inside the 40 s target, before OCR time.

Decision: ADR-007. Design consequences for Story 3.2 are listed there.

## 6. Memory

Peak resident memory, each measured in a fresh process on macOS arm64:

| Component | Peak RSS |
|---|---|
| Python + FastAPI + Uvicorn + Pydantic | 47 MB |
| + PyMuPDF and OpenCV imported | 110 MB |
| Tesseract child process, one page at 200 dpi | 118 MB |
| Tesseract child process, one page at 300 dpi | 188 MB |
| `multilingual-e5-small` embedding model | not measured |

Server plus one OCR page is about 230 MB of the 512 MB. The embedding model was not
measured: the model files were not downloaded, and Ollama's library does not carry this
model. Its fp32 weights alone are about 470 MB (about 118 M parameters), so only a
quantised build can fit. Decision and next step: ADR-008.

## 7. Reproduce

```bash
brew install tesseract tesseract-lang
cd backend && .venv/bin/pip install -e ".[dev,spike]" && cd ..
python eval/corpus.py fetch                    # restore the PDFs
python eval/spike.py text                      # sections 2–3
python eval/spike.py llm gemma3:4b             # section 5 (Ollama must be running)
python eval/spike.py llm gemma3:4b --variant v2
python eval/spike.py ram                       # section 6
```
