# ADR-006: Bijoy-encoded PDFs go through OCR in v1; no converter yet
Status: accepted (provisional) · 2026-11-16
Decision: When most of a PDF's text is set in a Bijoy font (SutonnyMJ and other `*MJ`
fonts), v1 ignores the text layer and sends the rendered pages to Tesseract, the same path
as a scan. We do not ship a Bijoy→Unicode converter in v1. Bijoy is detected per text span
by font name, not per document.
Why: a rendered Bijoy page shows correct Bangla glyphs, and Tesseract read the one real
Bijoy-font document we found correctly. The off-the-shelf converter (`bijoy2unicode` 0.1.1
from PyPI) made three kinds of error in 1,306 characters of that document: misplaced reph
(রেজিস্টাডর্ for রেজিস্টার্ড), an unmapped ক্ষ (কতৃর্পÿ for কর্তৃপক্ষ) and a wrong conjunct
(ফেব্রম্নয়ারি for ফেব্রুয়ারি). Errors like these would corrupt post titles and dates, and
the evidence-quote check would then reject correct facts. One code path is also simpler.
Evidence is thin: the test corpus has no Bijoy circular (none on 71 gov.bd sites; two
sweeps), only one gazette that is 4% Bijoy. That is why this is provisional.
Trade-off: Bijoy files pay OCR time and OCR error instead of a fast exact conversion.
Revisit if: the owner supplies real Bijoy circulars. Then compare OCR against our own
mapping table (written with reph and vowel-sign reordering, tested on those files) and
switch if the table is more accurate.
