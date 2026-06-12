#!/usr/bin/env python3
"""
patch_reader_wordmark_toggle.py — show the centered Fablewick wordmark on the
cover only.

Mann: remove the wordmark from the top-bar center once you're into the story.
So: visible on the cover (page 1, the title page), hidden on all story/end
pages. One line added to updateUI(); idempotent.

Run:  python scripts/patch_reader_wordmark_toggle.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "library"

ANCHOR = "  if (flipNext) flipNext.disabled = currentIdx === total - 1;"
ADD = (
    ANCHOR + "\n"
    "  var _wm = document.querySelector('.topbar-wordmark');\n"
    "  if (_wm) _wm.style.display = currentIdx === 0 ? '' : 'none';"
)


def patch(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if "_wm = document.querySelector('.topbar-wordmark')" in text:
        return "skip (already toggled)"
    if text.count(ANCHOR) != 1:
        raise RuntimeError(f"{path.name}: updateUI anchor not unique (n={text.count(ANCHOR)})")
    text = text.replace(ANCHOR, ADD, 1)
    path.write_text(text, encoding="utf-8")
    return "patched"


def main():
    readers = sorted(LIB.glob("reader-*.html"))
    if not readers:
        sys.exit(f"ERROR: no readers in {LIB}")
    print("Fablewick wordmark: cover-only toggle")
    for r in readers:
        print(f"  {r.name:48s} {patch(r)}")
    print("Done.")


if __name__ == "__main__":
    main()
