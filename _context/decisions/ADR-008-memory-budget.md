# ADR-008: Memory plan for the 512 MB backend
Status: accepted for OCR; embedding part open · 2026-11-16
Decision:
1. Tesseract runs as a child process, one page at a time, one thread (`OMP_THREAD_LIMIT=1`),
   at 200 dpi. Pages are never OCRed in parallel on the server.
2. No OpenCV in the runtime image (ADR-005 found no accuracy gain from it).
3. Heavy modules (PyMuPDF, the embedding model) are imported lazily, on first use, so
   `/health` and auth stay light.
4. The embedding model must not be loaded as fp32 PyTorch. The planned route is the int8
   ONNX build of `multilingual-e5-small` on `onnxruntime`; this is **not yet measured**.
Why (measured on macOS arm64, docs/SPIKE.md): Python + FastAPI is 47 MB; with PyMuPDF and
OpenCV imported, 110 MB; a Tesseract page at 200 dpi peaks at 118 MB (188 MB at 300 dpi).
So the server plus one OCR page is about 230 MB, leaving roughly 280 MB for embeddings and
request data. `multilingual-e5-small` has about 118 M parameters, so its fp32 weights alone
are about 470 MB and cannot fit; an int8 build should be near 120 MB plus runtime overhead.
Open: the embedding model's real peak memory. The owner declined the Hugging Face download
during the spike, and the Ollama library does not carry this model. Measure before Story 3.1
with `python eval/spike.py ram` once the model files are in `eval/results/e5-small/`.
Revisit if: the int8 model does not fit or hurts retrieval quality. Fallbacks, in order:
embed in a separate free service; switch to a smaller multilingual model (new ADR).
Caveat: numbers are from a Mac; Linux RSS on Render will differ somewhat. Re-check on the
first deploy.
