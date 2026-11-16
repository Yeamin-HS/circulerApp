# ADR-005: Tesseract `ben+eng` at 200 dpi is the v1 OCR engine
Status: accepted · 2026-11-16
Decision: Scanned circulars are rendered with PyMuPDF at 200 dpi and read by the Tesseract
CLI (`-l ben+eng`, default page segmentation, stock `tessdata_fast` models), one page at a
time, one thread. No OpenCV deskew/binarise step in v1. No second OCR engine.
Why: on the 12 scanned test circulars it recovers 98% of the labelled facts by fuzzy match
and 85% exactly (docs/SPIKE.md). 200 dpi scores the same as 300 dpi while using 118 MB peak
instead of 188 MB and less time. OpenCV preprocessing and `--psm 6` both scored slightly
lower, so they are not worth the extra dependency and code. Tesseract runs as a child
process, so its memory is released after each page.
Also decided: a text layer is used only when it passes the usability checks in the spike's
`detect()` (enough Bangla Unicode with intact vowel signs, or clean English). Garbled
Unicode and junk OCR layers go to Tesseract; 3 of our 15 files need this.
Trade-off: table rows are read as loose lines, so column structure is lost; the LLM has to
re-associate posts with vacancies. Speed on Render's shared CPU is not measured yet.
Revisit if: fact-card accuracy on scanned files stays under the NFR-03 target because of OCR
errors, or OCR time on Render breaks the 40 s target (NFR-05).
