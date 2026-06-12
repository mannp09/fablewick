#!/usr/bin/env python3
"""
patch_reader_remove_wordmark.py — remove the centered Fablewick wordmark from
the reader top bar entirely (cover included), per Mann.

Removes the wordmark <img> and reverts the SIZE TUNE block (the taller top bar
existed only to fit the wordmark), restoring the original 52px bar offsets.
The top bar becomes: flame mark -> home (left) · page counter (right).
Idempotent.

Run:  python scripts/patch_reader_remove_wordmark.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "library"

WORDMARK_IMG = '<img class="topbar-wordmark" src="../src/assets/fablewick-logo.png" alt="Fablewick">'

SIZE_TUNE_BLOCK = """
/* ── SIZE TUNE: larger centered wordmark + taller top bar ─────── */
.book-topbar { height: 64px; }
.progress-track { top: 64px; }
.stage { top: 67px; }
.book-topbar .topbar-wordmark { height: 44px; }
.flip-zone { top: 70px; }
@media (max-width: 560px) {
  .book-topbar { height: 56px; }
  .progress-track { top: 56px; }
  .stage { top: 59px; }
  .book-topbar .topbar-wordmark { height: 34px; }
  .flip-zone { top: 62px; }
}
"""


def patch(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if WORDMARK_IMG not in text:
        return "skip (no wordmark)"
    text = text.replace(WORDMARK_IMG, "", 1)
    if SIZE_TUNE_BLOCK in text:
        text = text.replace(SIZE_TUNE_BLOCK, "", 1)
    path.write_text(text, encoding="utf-8")
    return "wordmark removed + bar reverted"


def main():
    readers = sorted(LIB.glob("reader-*.html"))
    if not readers:
        sys.exit(f"ERROR: no readers in {LIB}")
    print("Fablewick: remove topbar wordmark")
    for r in readers:
        print(f"  {r.name:48s} {patch(r)}")
    print("Done.")


if __name__ == "__main__":
    main()
