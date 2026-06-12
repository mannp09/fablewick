#!/usr/bin/env python3
"""Validate every book in src/content/books/.

Checks structure, required fields, word counts (within tolerance), and surfaces
common mistakes (missing levels, malformed JSON, ageRange flipped, etc.).

Run from repo root:
    python scripts/validate-books.py
"""

import io
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BOOKS_DIR = Path(__file__).parent.parent / "src" / "content" / "books"

LEVEL_TARGETS = {
    "1": ("Little Listener", 150, 250),
    "2": ("New Reader", 400, 600),
    "3": ("On Your Own", 800, 1200),
}

REQUIRED_FIELDS = ("title", "ageRange", "themes", "lesson", "summary", "coverColor", "coverIllustration", "levels")


def warn(msg: str) -> None:
    print(f"  ! {msg}")


def err(msg: str) -> None:
    print(f"  ✗ {msg}")


def validate_book(meta_path: Path) -> tuple[int, int]:
    """Return (errors, warnings) for one book."""
    errors = warnings = 0
    print(f"\n{meta_path.parent.name}/")

    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"meta.json is not valid JSON: {e}")
        return 1, 0

    for field in REQUIRED_FIELDS:
        if field not in data:
            err(f"missing required field: {field}")
            errors += 1

    age = data.get("ageRange")
    if isinstance(age, list) and len(age) == 2:
        if age[0] > age[1]:
            err(f"ageRange is flipped: {age}")
            errors += 1
        if age[0] < 2 or age[1] > 12:
            warn(f"ageRange {age} is outside 2-12 (intended scope)")
            warnings += 1

    themes = data.get("themes")
    if isinstance(themes, list) and len(themes) == 0:
        warn("themes list is empty")
        warnings += 1

    levels = data.get("levels", {})
    for key, (label, lo, hi) in LEVEL_TARGETS.items():
        if key not in levels:
            err(f"missing level {key} ({label})")
            errors += 1
            continue
        level = levels[key]
        text = level.get("text", "")
        if not text:
            err(f"level {key} has no text")
            errors += 1
            continue
        words = len(text.split())
        if not (lo <= words <= hi):
            warn(f"level {key} word count {words} outside target {lo}-{hi}")
            warnings += 1
        if level.get("label") != label:
            warn(f"level {key} label is '{level.get('label')}', expected '{label}'")
            warnings += 1

    if errors == 0 and warnings == 0:
        print("  ✓ clean")

    return errors, warnings


def main() -> int:
    if not BOOKS_DIR.exists():
        print(f"Books directory not found: {BOOKS_DIR}")
        return 1

    meta_files = sorted(BOOKS_DIR.glob("*/meta.json"))
    if not meta_files:
        print("No books found.")
        return 0

    print(f"Validating {len(meta_files)} book(s)...")
    total_errors = total_warnings = 0
    for meta in meta_files:
        e, w = validate_book(meta)
        total_errors += e
        total_warnings += w

    print(f"\n{'=' * 40}")
    print(f"Books: {len(meta_files)}  Errors: {total_errors}  Warnings: {total_warnings}")
    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
