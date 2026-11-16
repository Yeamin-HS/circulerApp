"""Test-corpus helper (Story 1.2). Standard library only.

    python eval/corpus.py check    validate eval/labels/*.json and report corpus coverage
    python eval/corpus.py fetch    download missing circulars from each label's source_url

Circular files are gitignored, so `fetch` is how another machine restores them.
"""

import hashlib
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

EVAL = Path(__file__).parent
LABELS = EVAL / "labels"
CIRCULARS = EVAL / "circulars"

SOURCE_TYPES = {"digital", "scanned", "bijoy"}
TEXT_LAYERS = {"unicode", "garbled_unicode", "junk_ocr", "none"}
LANGUAGES = {"bn", "en", "mixed"}
APPLY_MODES = {"online", "post_or_in_person", "email_or_in_person"}
DEGREES = {"Class 8", "JSC", "SSC", "HSC", "Diploma", "Bachelor", "Masters", "PhD"}

# ARCHITECTURE §9: 12-15 circulars, >= 3 scanned, >= 2 Bijoy, >= 3 multi-post.
TARGETS = {"total": 12, "scanned": 3, "bijoy": 2, "multi_post": 3}


def load() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(LABELS.glob("*.json"))]


def _is_date(value: object) -> bool:
    try:
        date.fromisoformat(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False
    return True


def _opt(value: object, kind: type | tuple[type, ...]) -> bool:
    return value is None or (isinstance(value, kind) and not isinstance(value, bool))


def errors_in(label: dict) -> list[str]:
    errs: list[str] = []

    def need(ok: bool, msg: str) -> None:
        if not ok:
            errs.append(msg)

    need(label.get("file") == f"{label.get('id')}.pdf", "file must be <id>.pdf")
    need(label.get("source_type") in SOURCE_TYPES, "bad source_type")
    need(label.get("text_layer") in TEXT_LAYERS, "bad text_layer")
    need(label.get("language") in LANGUAGES, "bad language")
    need(isinstance(label.get("verified"), bool), "verified must be true/false")
    need(str(label.get("source_url", "")).startswith("http"), "source_url missing")

    card = label.get("fact_card") or {}
    posts = card.get("posts") or []
    need(isinstance(card.get("organisation"), str), "organisation missing")
    need(len(posts) >= 1, "at least one post required")
    need(label.get("multi_post") == (len(posts) > 1), "multi_post does not match posts")
    need(card.get("deadline") is None or _is_date(card["deadline"]), "deadline not ISO date")
    need(card.get("age_as_of") is None or _is_date(card["age_as_of"]), "age_as_of not ISO date")
    need(_opt(card.get("age_limit"), int), "age_limit must be int or null")
    need(_opt(card.get("fee"), str), "fee must be string or null")
    need(card.get("apply_mode") in APPLY_MODES, "bad apply_mode")
    need(_opt(card.get("apply_link"), str), "apply_link must be string or null")
    for i, post in enumerate(posts, 1):
        need(bool(post.get("title")), f"post {i}: title missing")
        need(_opt(post.get("vacancies"), int), f"post {i}: vacancies must be int or null")
        need(post.get("min_degree") in DEGREES | {None}, f"post {i}: bad min_degree")
        need(_opt(post.get("subjects"), list), f"post {i}: subjects must be list or null")
        need(_opt(post.get("experience_years"), (int, float)), f"post {i}: bad experience_years")
        need(_opt(post.get("age_limit"), int), f"post {i}: age_limit must be int or null")
    return errs


def check() -> int:
    labels = load()
    failed = 0
    for label in labels:
        errs = errors_in(label)
        path = CIRCULARS / str(label.get("file"))
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != label.get("sha256"):
            errs.append("file on disk does not match sha256")
        for err in errs:
            print(f"ERROR {label.get('id')}: {err}")
        failed += bool(errs)

    counts = {
        "total": len(labels),
        "scanned": sum(x["source_type"] == "scanned" for x in labels),
        "bijoy": sum(x["source_type"] == "bijoy" for x in labels),
        "multi_post": sum(bool(x.get("multi_post")) for x in labels),
    }
    print(f"{len(labels)} labels, {failed} with errors")
    for key, target in TARGETS.items():
        mark = "ok " if counts[key] >= target else "GAP"
        print(f"  {mark} {key}: {counts[key]} (target >= {target})")
    print(f"  digital: {sum(x['source_type'] == 'digital' for x in labels)}")
    print(f"  owner-verified: {sum(x['verified'] for x in labels)} of {len(labels)}")
    missing = [x["file"] for x in labels if not (CIRCULARS / x["file"]).exists()]
    if missing:
        print(f"  {len(missing)} circular file(s) not on disk; run: python eval/corpus.py fetch")
    return 1 if failed else 0


def fetch() -> int:
    CIRCULARS.mkdir(exist_ok=True)
    bad = 0
    for label in load():
        path = CIRCULARS / label["file"]
        if path.exists():
            continue
        request = urllib.request.Request(label["source_url"], headers={"User-Agent": "Mozilla/5.0"})
        try:
            data = urllib.request.urlopen(request, timeout=90).read()
        except OSError as exc:
            print(f"FAILED {label['id']}: {exc}")
            bad += 1
            continue
        if hashlib.sha256(data).hexdigest() != label["sha256"]:
            print(f"FAILED {label['id']}: source file changed (sha256 mismatch), not saved")
            bad += 1
            continue
        path.write_bytes(data)
        print(f"saved {path.name}")
    return 1 if bad else 0


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command not in {"check", "fetch"}:
        sys.exit(__doc__)
    sys.exit(check() if command == "check" else fetch())
