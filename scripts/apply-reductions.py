#!/usr/bin/env python3
"""
apply-reductions.py

Wave: text apply (English). Fablewick v2.

Parses the two Mann-approved reduction drafts:
  docs/text-reduction-fablewick-2026-09-04.md   (11 readers, languages only)
  docs/text-reduction-ramkabir-2026-09-04.md    (5 Ramkabir stories, 3 levels)

and applies the reduced ENGLISH text into the sources:
  library/reader-<slug>.i18n.json   pageTexts.en[i] / covers.en / ends.en
  library/ramkabir-fablewick.html   the `const BOOKS = [...]` literal, per level

Before writing any page, the doc's "original text" column is compared
(whitespace normalised) against the text currently on disk. A mismatch is
refused and reported rather than guessed at -- that page is left untouched.

After writing, every source file touched is re-read from disk and every
written page is asserted to be no longer, in whitespace-token words, than
the word count recorded for it before the write.

Usage:
    python scripts/apply-reductions.py            # apply for real
    python scripts/apply-reductions.py --dry-run  # parse + diff only, write nothing

Run from the repo root (C:/Users/mann0/Desktop/mann-studio/fablewick).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOC_FABLEWICK = REPO / "docs" / "text-reduction-fablewick-2026-09-04.md"
DOC_RAMKABIR = REPO / "docs" / "text-reduction-ramkabir-2026-09-04.md"
LIBRARY_DIR = REPO / "library"
RAMKABIR_HTML = LIBRARY_DIR / "ramkabir-fablewick.html"

BR_BR_PLACEHOLDER = "\x00PARA\x00"


def br_to_newlines(text: str) -> str:
    """<br><br> -> \\n\\n (paragraph break); a lone <br> -> \\n (line break inside a device)."""
    text = text.replace("<br><br>", BR_BR_PLACEHOLDER)
    text = text.replace("<br>", "\n")
    text = text.replace(BR_BR_PLACEHOLDER, "\n\n")
    return text


def normalize_ws(text: str) -> str:
    """Collapse all whitespace runs to a single space, for comparison only."""
    return re.sub(r"\s+", " ", text).strip()


def word_count(text: str) -> int:
    return len(text.split())


# ---------------------------------------------------------------------------
# Table parsing (shared)
# ---------------------------------------------------------------------------

def is_separator_row(cells: list[str]) -> bool:
    joined = "".join(cells)
    return bool(joined) and set(joined) <= set("-: ")


def parse_rows(body: str, expected_cols: int):
    """Yield list[str] cells for each real data row of the first/only table in `body`."""
    rows = []
    header_seen = False
    for line in body.splitlines():
        line = line.rstrip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) != expected_cols:
            continue
        if is_separator_row(cells):
            continue
        if not header_seen:
            # first table row is the header (e.g. "page" / "Page")
            header_seen = True
            continue
        rows.append(cells)
    return rows


PAGE_CELL_RE = re.compile(r"^(\S+)(?:\s*\*\(already tight\)\*)?\s*$")


def parse_page_cell(cell: str):
    m = PAGE_CELL_RE.match(cell)
    if not m:
        # fall back: first whitespace-delimited token
        return cell.split()[0], "already tight" in cell
    return m.group(1), "already tight" in cell


def parse_int(s: str) -> int:
    return int(re.sub(r"[^\d]", "", s))


# ---------------------------------------------------------------------------
# Fablewick doc parsing
# ---------------------------------------------------------------------------

FABLEWICK_HEADER_RE = re.compile(r"^(.+?) \(`([a-z0-9-]+)`\)\s*$")


def parse_fablewick_doc(path: Path):
    text = path.read_text(encoding="utf-8")
    headers = list(re.finditer(r"(?m)^## (.+)$", text))
    stories = {}  # slug -> list of page dicts
    for i, h in enumerate(headers):
        m = FABLEWICK_HEADER_RE.match(h.group(1).strip())
        if not m:
            continue
        slug = m.group(2)
        start = h.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        body = text[start:end]
        pages = []
        for cells in parse_rows(body, 5):
            page_cell, tight = parse_page_cell(cells[0])
            pages.append({
                "page": page_cell,
                "tight": tight,
                "orig_words": parse_int(cells[1]),
                "reduced_words": parse_int(cells[2]),
                "original": br_to_newlines(cells[3]),
                "reduced": br_to_newlines(cells[4]),
            })
        stories[slug] = pages
    return stories


# ---------------------------------------------------------------------------
# Ramkabir doc parsing
# ---------------------------------------------------------------------------

SLUG_LINE_RE = re.compile(r"\*Slug: `([a-z0-9-]+)`\.")
LEVEL_HEADER_RE = re.compile(r"^(Kids|Adults|Seniors)\s*$")


def parse_ramkabir_doc(path: Path):
    text = path.read_text(encoding="utf-8")
    top_headers = list(re.finditer(r"(?m)^## (.+)$", text))
    stories = {}  # slug -> {level: [page dicts]}
    for i, h in enumerate(top_headers):
        title = h.group(1).strip()
        start = h.end()
        end = top_headers[i + 1].start() if i + 1 < len(top_headers) else len(text)
        body = text[start:end]
        slug_m = SLUG_LINE_RE.search(body)
        if not slug_m:
            continue  # "Summary" / "What was deliberately not cut" sections
        slug = slug_m.group(1)

        level_headers = list(re.finditer(r"(?m)^### (Kids|Adults|Seniors)\s*$", body))
        levels = {}
        for j, lh in enumerate(level_headers):
            level_name = lh.group(1).lower()
            lstart = lh.end()
            lend = level_headers[j + 1].start() if j + 1 < len(level_headers) else len(body)
            lbody = body[lstart:lend]
            pages = []
            for cells in parse_rows(lbody, 5):
                page_cell, tight = parse_page_cell(cells[0])
                pages.append({
                    "page": page_cell,
                    "tight": tight,
                    "orig_words": parse_int(cells[1]),
                    "reduced_words": parse_int(cells[2]),
                    "original": br_to_newlines(cells[3]),
                    "reduced": br_to_newlines(cells[4]),
                })
            levels[level_name] = pages
        stories[slug] = levels
    return stories


# ---------------------------------------------------------------------------
# JSON I/O that preserves the exact on-disk formatting (verified byte-identical
# round trip: indent=2, ensure_ascii=False, CRLF line endings, no trailing newline)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Apply: Fablewick
# ---------------------------------------------------------------------------

def apply_fablewick(stories: dict, dry_run: bool):
    applied = 0
    skipped = []
    unchanged = 0

    for slug, pages in stories.items():
        try:
            path, data = load_reader_json(slug)
        except FileNotFoundError:
            for p in pages:
                skipped.append((slug, p["page"], "source file not found: reader-%s.i18n.json" % slug))
            continue

        touched = False
        pre_lengths = {}  # (field) -> word count of the ON-DISK text before this run

        for p in pages:
            page_id = p["page"]
            if page_id == "cover":
                field_get = lambda: data["covers"]["en"]
                field_set = lambda v: data["covers"].__setitem__("en", v)
            elif page_id == "end":
                field_get = lambda: data["ends"]["en"]
                field_set = lambda v: data["ends"].__setitem__("en", v)
            else:
                try:
                    idx = int(page_id) - 1
                except ValueError:
                    skipped.append((slug, page_id, f"unrecognized page id '{page_id}'"))
                    continue
                if idx < 0 or idx >= len(data["pageTexts"]["en"]):
                    skipped.append((slug, page_id, f"page index {idx} out of range (0..{len(data['pageTexts']['en'])-1})"))
                    continue
                field_get = (lambda idx=idx: data["pageTexts"]["en"][idx])
                field_set = (lambda v, idx=idx: data["pageTexts"]["en"].__setitem__(idx, v))

            current = field_get()
            if normalize_ws(current) != normalize_ws(p["original"]):
                skipped.append((slug, page_id, "MISMATCH: doc's 'original text' does not match the source on disk"))
                continue

            pre_lengths[(slug, page_id)] = word_count(current)

            if normalize_ws(current) == normalize_ws(p["reduced"]):
                unchanged += 1
                continue

            if not dry_run:
                field_set(p["reduced"])
            touched = True
            applied += 1

        if touched and not dry_run:
            dump_reader_json(path, data)

    return applied, unchanged, skipped


# ---------------------------------------------------------------------------
# Apply: Ramkabir
# ---------------------------------------------------------------------------

def apply_ramkabir(stories: dict, dry_run: bool):
    applied = 0
    skipped = []
    unchanged = 0

    if not RAMKABIR_HTML.exists():
        for slug, levels in stories.items():
            for level, pages in levels.items():
                for p in pages:
                    skipped.append((slug, f"{level} p{p['page']}", "ramkabir-fablewick.html not found"))
        return applied, unchanged, skipped

    content, books = load_books(RAMKABIR_HTML)
    by_slug = {b["slug"]: b for b in books}
    touched = False

    for slug, levels in stories.items():
        book = by_slug.get(slug)
        if book is None:
            for level, pages in levels.items():
                for p in pages:
                    skipped.append((slug, f"{level} p{p['page']}", "slug not found in BOOKS literal"))
            continue

        for level, pages in levels.items():
            if level not in book["levels"]:
                for p in pages:
                    skipped.append((slug, f"{level} p{p['page']}", f"level '{level}' not found for this book"))
                continue
            en_pages = book["levels"][level]["en"]
            for p in pages:
                page_id = p["page"]
                try:
                    idx = int(page_id) - 1
                except ValueError:
                    skipped.append((slug, f"{level} p{page_id}", f"unrecognized page id '{page_id}'"))
                    continue
                if idx < 0 or idx >= len(en_pages):
                    skipped.append((slug, f"{level} p{page_id}", f"page index {idx} out of range (0..{len(en_pages)-1})"))
                    continue

                current = en_pages[idx]
                if normalize_ws(current) != normalize_ws(p["original"]):
                    skipped.append((slug, f"{level} p{page_id}", "MISMATCH: doc's 'original text' does not match the source on disk"))
                    continue

                if normalize_ws(current) == normalize_ws(p["reduced"]):
                    unchanged += 1
                    continue

                if not dry_run:
                    en_pages[idx] = p["reduced"]
                touched = True
                applied += 1

    if touched and not dry_run:
        dump_books(RAMKABIR_HTML, content, books)

    return applied, unchanged, skipped


# ---------------------------------------------------------------------------
# Post-write verification: every touched page must be <= its pre-write length
# ---------------------------------------------------------------------------

def verify_fablewick(stories: dict):
    problems = []
    checked = 0
    for slug, pages in stories.items():
        path = LIBRARY_DIR / f"reader-{slug}.i18n.json"
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        for p in pages:
            page_id = p["page"]
            if page_id == "cover":
                now = data["covers"]["en"]
            elif page_id == "end":
                now = data["ends"]["en"]
            else:
                try:
                    idx = int(page_id) - 1
                except ValueError:
                    continue
                if idx < 0 or idx >= len(data["pageTexts"]["en"]):
                    continue
                now = data["pageTexts"]["en"][idx]
            checked += 1
            if word_count(now) > p["orig_words"]:
                problems.append((slug, page_id, word_count(now), p["orig_words"]))
    return checked, problems


def verify_ramkabir(stories: dict):
    problems = []
    checked = 0
    if not RAMKABIR_HTML.exists():
        return checked, problems
    _, books = load_books(RAMKABIR_HTML)
    by_slug = {b["slug"]: b for b in books}
    for slug, levels in stories.items():
        book = by_slug.get(slug)
        if book is None:
            continue
        for level, pages in levels.items():
            if level not in book["levels"]:
                continue
            en_pages = book["levels"][level]["en"]
            for p in pages:
                try:
                    idx = int(p["page"]) - 1
                except ValueError:
                    continue
                if idx < 0 or idx >= len(en_pages):
                    continue
                checked += 1
                now = en_pages[idx]
                if word_count(now) > p["orig_words"]:
                    problems.append((slug, f"{level} p{p['page']}", word_count(now), p["orig_words"]))
    return checked, problems


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="parse and diff only, write nothing")
    args = ap.parse_args()

    fablewick_stories = parse_fablewick_doc(DOC_FABLEWICK)
    ramkabir_stories = parse_ramkabir_doc(DOC_RAMKABIR)

    fw_pages_in_doc = sum(len(v) for v in fablewick_stories.values())
    rk_pages_in_doc = sum(len(pp) for lv in ramkabir_stories.values() for pp in lv.values())

    print(f"Parsed Fablewick doc: {len(fablewick_stories)} stories, {fw_pages_in_doc} page rows")
    print(f"Parsed Ramkabir doc:  {len(ramkabir_stories)} stories, {rk_pages_in_doc} page rows (all levels)")
    print()

    fw_applied, fw_unchanged, fw_skipped = apply_fablewick(fablewick_stories, args.dry_run)
    rk_applied, rk_unchanged, rk_skipped = apply_ramkabir(ramkabir_stories, args.dry_run)

    mode = "DRY RUN (nothing written)" if args.dry_run else "APPLIED"
    print(f"=== {mode} ===")
    print()
    print("Fablewick (English):")
    print(f"  applied (changed):   {fw_applied}")
    print(f"  unchanged (no diff): {fw_unchanged}")
    print(f"  skipped:             {len(fw_skipped)}")
    for slug, page, reason in fw_skipped:
        print(f"    - {slug} / {page}: {reason}")
    print()
    print("Ramkabir (English, all 3 levels):")
    print(f"  applied (changed):   {rk_applied}")
    print(f"  unchanged (no diff): {rk_unchanged}")
    print(f"  skipped:             {len(rk_skipped)}")
    for slug, page, reason in rk_skipped:
        print(f"    - {slug} / {page}: {reason}")
    print()

    if not args.dry_run:
        fw_checked, fw_problems = verify_fablewick(fablewick_stories)
        rk_checked, rk_problems = verify_ramkabir(ramkabir_stories)
        print("=== Post-write verification (reduced word count <= original word count) ===")
        print(f"Fablewick: {fw_checked} pages checked, {len(fw_problems)} problems")
        for slug, page, now_wc, orig_wc in fw_problems:
            print(f"    ! {slug} / {page}: now {now_wc} words > recorded original {orig_wc} words")
        print(f"Ramkabir:  {rk_checked} pages checked, {len(rk_problems)} problems")
        for slug, page, now_wc, orig_wc in rk_problems:
            print(f"    ! {slug} / {page}: now {now_wc} words > recorded original {orig_wc} words")
        if fw_problems or rk_problems:
            sys.exit(1)

    total_skipped = len(fw_skipped) + len(rk_skipped)
    if total_skipped:
        print(f"\n{total_skipped} page(s) skipped -- see reasons above. Nothing was guessed at.")


if __name__ == "__main__":
    main()
