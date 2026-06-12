#!/usr/bin/env python3
"""
patch_reader_sizetune.py — enlarge the centered Fablewick wordmark.

Mann: the topbar wordmark was too small. The 52px bar capped it at 26px.
This grows the bar (52->64 / mobile 56), the wordmark (26->44 / mobile 34),
and re-coordinates the progress-track, stage, and flip-zone top offsets so
nothing overlaps. Appended as an override block (later rules win); idempotent.

Run:  python scripts/patch_reader_sizetune.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "library"

TUNE = """
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
    if "SIZE TUNE" in text:
        return "skip (already tuned)"
    if "</style>" not in text:
        raise RuntimeError(f"{path.name}: no </style>")
    text = text.replace("</style>", TUNE + "</style>", 1)
    path.write_text(text, encoding="utf-8")
    return "tuned"


def main():
    readers = sorted(LIB.glob("reader-*.html"))
    if not readers:
        sys.exit(f"ERROR: no readers in {LIB}")
    print("Fablewick wordmark size tune")
    for r in readers:
        print(f"  {r.name:48s} {patch(r)}")
    print("Done.")


if __name__ == "__main__":
    main()
