#!/usr/bin/env python3
"""
apply-translations.py

Wave: text apply (translations). Fablewick v2.

Applies translated, reduced non-English text -- produced by hand to match the
English reductions already applied by apply-reductions.py -- into the sources:

  library/reader-<slug>.i18n.json   pageTexts.<lang>[i] / covers.<lang> / ends.<lang>
  library/ramkabir-fablewick.html   the `const BOOKS = [...]` literal, per level, per lang

Input is one or more "patch" JSON files of the shape:

{
  "fablewick": {
    "<slug>": {
      "<lang>": {
        "cover": "...",          # optional
        "end": "...",            # optional
        "pages": {"1": "...", "3": "..."}   # 1-indexed page numbers, optional
      }
    }
  },
  "ramkabir": {
    "<slug>": {
      "<level>": {
        "<lang>": {"1": "...", "2": "..."}   # 1-indexed page numbers
      }
    }
  }
}

Only "hi", "gu" (Ramkabir) and "hi", "gu", "es", "fr" (Fablewick) are valid
target languages -- "en" is refused (English goes through apply-reductions.py).

For every item, the OLD translation's character length is read from disk
before the write, and the NEW text's length is asserted to be no more than
5% longer (in characters) than the old one. An item over that bound is
still applied (a genuine meaning-preserving translation is allowed to run
long) but is flagged in the printed report rather than applied silently.

Usage:
    python scripts/apply-translations.py patch1.json [patch2.json ...]
    python scripts/apply-translations.py --dry-run patch1.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LIBRARY_DIR = REPO / "library"
RAMKABIR_HTML = LIBRARY_DIR / "ramkabir-fablewick.html"

FABLEWICK_LANGS = {"hi", "gu", "es", "fr"}
RAMKABIR_LANGS = {"hi", "gu"}
OVERAGE_ALLOWED = 1.05


def load_reader_json(slug: str):
    path = LIBRARY_DIR / f"reader-{slug}.i18n.json"
    with path.open(encoding="utf-8") as f:
        return path, json.load(f)


def dump_reader_json(path: Path, data) -> None:
    s = json.dumps(data, indent=2, ensure_ascii=False)
    s = s.replace("\n", "\r\n")
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write(s)


BOOKS_RE = re.compile(r"const BOOKS = (\[.*?\]);\nconst LEVELS", re.S)


def load_books(path: Path):
    content = path.read_text(encoding="utf-8")
    m = BOOKS_RE.search(content)
    if not m:
        raise RuntimeError(f"could not find `const BOOKS = [...]` literal in {path}")
    return content, json.loads(m.group(1))


def dump_books(path: Path, content: str, books) -> None:
    new_array = json.dumps(books, ensure_ascii=False)
    new_content = BOOKS_RE.sub(lambda _m: f"const BOOKS = {new_array};\nconst LEVELS", content, count=1)
    path.write_text(new_content, encoding="utf-8")


def apply_fablewick_patch(patch: dict, dry_run: bool, report: list):
    applied = 0
    flagged = 0
    errors = 0
    for slug, langs in patch.items():
        try:
            path, data = load_reader_json(slug)
        except FileNotFoundError:
            report.append(("ERROR", slug, "-", "-", f"source not found: reader-{slug}.i18n.json"))
            errors += 1
            continue

        touched = False
        for lang, fields in langs.items():
            if lang not in FABLEWICK_LANGS:
                report.append(("ERROR", slug, lang, "-", f"'{lang}' is not a valid Fablewick target language"))
                errors += 1
                continue

            if "cover" in fields:
                old = data["covers"].get(lang)
                if old is None:
                    report.append(("ERROR", slug, lang, "cover", "no existing cover for this language"))
                    errors += 1
                else:
                    new = fields["cover"]
                    ratio = len(new) / max(1, len(old))
                    if ratio > OVERAGE_ALLOWED:
                        report.append(("FLAG", slug, lang, "cover", f"{len(old)} -> {len(new)} chars ({ratio:.2f}x)"))
                        flagged += 1
                    if not dry_run:
                        data["covers"][lang] = new
                    touched = True
                    applied += 1

            if "end" in fields:
                old = data["ends"].get(lang)
                if old is None:
                    report.append(("ERROR", slug, lang, "end", "no existing end for this language"))
                    errors += 1
                else:
                    new = fields["end"]
                    ratio = len(new) / max(1, len(old))
                    if ratio > OVERAGE_ALLOWED:
                        report.append(("FLAG", slug, lang, "end", f"{len(old)} -> {len(new)} chars ({ratio:.2f}x)"))
                        flagged += 1
                    if not dry_run:
                        data["ends"][lang] = new
                    touched = True
                    applied += 1

            for page_str, new in fields.get("pages", {}).items():
                idx = int(page_str) - 1
                arr = data["pageTexts"].get(lang)
                if arr is None:
                    report.append(("ERROR", slug, lang, page_str, "no existing pageTexts array for this language"))
                    errors += 1
                    continue
                if idx < 0 or idx >= len(arr):
                    report.append(("ERROR", slug, lang, page_str, f"page index {idx} out of range"))
                    errors += 1
                    continue
                old = arr[idx]
                ratio = len(new) / max(1, len(old))
                if ratio > OVERAGE_ALLOWED:
                    report.append(("FLAG", slug, lang, page_str, f"{len(old)} -> {len(new)} chars ({ratio:.2f}x)"))
                    flagged += 1
                if not dry_run:
                    arr[idx] = new
                touched = True
                applied += 1

        if touched and not dry_run:
            dump_reader_json(path, data)

    return applied, flagged, errors


def apply_ramkabir_patch(patch: dict, dry_run: bool, report: list):
    applied = 0
    flagged = 0
    errors = 0

    if not patch:
        return applied, flagged, errors

    content, books = load_books(RAMKABIR_HTML)
    by_slug = {b["slug"]: b for b in books}
    touched = False

    for slug, levels in patch.items():
        book = by_slug.get(slug)
        if book is None:
            report.append(("ERROR", slug, "-", "-", "slug not found in BOOKS literal"))
            errors += 1
            continue
        for level, langs in levels.items():
            if level not in book["levels"]:
                report.append(("ERROR", slug, level, "-", f"level '{level}' not found"))
                errors += 1
                continue
            for lang, pages in langs.items():
                if lang not in RAMKABIR_LANGS:
                    report.append(("ERROR", slug, f"{level}/{lang}", "-", f"'{lang}' is not a valid Ramkabir target language"))
                    errors += 1
                    continue
                arr = book["levels"][level].get(lang)
                if arr is None:
                    report.append(("ERROR", slug, f"{level}/{lang}", "-", "no existing array for this language"))
                    errors += 1
                    continue
                for page_str, new in pages.items():
                    idx = int(page_str) - 1
                    if idx < 0 or idx >= len(arr):
                        report.append(("ERROR", slug, f"{level}/{lang}", page_str, f"page index {idx} out of range"))
                        errors += 1
                        continue
                    old = arr[idx]
                    ratio = len(new) / max(1, len(old))
                    if ratio > OVERAGE_ALLOWED:
                        report.append(("FLAG", slug, f"{level}/{lang}", page_str, f"{len(old)} -> {len(new)} chars ({ratio:.2f}x)"))
                        flagged += 1
                    if not dry_run:
                        arr[idx] = new
                    touched = True
                    applied += 1

    if touched and not dry_run:
        dump_books(RAMKABIR_HTML, content, books)

    return applied, flagged, errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("patches", nargs="+", help="patch JSON file(s)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    report = []
    total_applied = total_flagged = total_errors = 0

    for patch_path in args.patches:
        with open(patch_path, encoding="utf-8") as f:
            patch = json.load(f)
        fw = patch.get("fablewick", {})
        rk = patch.get("ramkabir", {})

        a, fl, er = apply_fablewick_patch(fw, args.dry_run, report)
        total_applied += a
        total_flagged += fl
        total_errors += er

        a, fl, er = apply_ramkabir_patch(rk, args.dry_run, report)
        total_applied += a
        total_flagged += fl
        total_errors += er

    mode = "DRY RUN" if args.dry_run else "APPLIED"
    print(f"=== {mode} ===")
    print(f"items applied: {total_applied}")
    print(f"items flagged (>5% longer in chars): {total_flagged}")
    print(f"errors: {total_errors}")
    print()
    for kind, slug, lang, page, detail in report:
        print(f"  [{kind}] {slug} / {lang} / {page}: {detail}")

    if total_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
