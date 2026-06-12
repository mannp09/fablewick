#!/usr/bin/env python3
"""Mobile-only reader nav fixes:
1. Hide the persistent white side flip-buttons on touch devices (keep tap zones live).
2. Stop the bottom "Page N of M" counter from wrapping on narrow phones.
Desktop behaviour is left unchanged.
"""
import pathlib
import sys

LIB = pathlib.Path(__file__).resolve().parent.parent / "library"

# 1. Side buttons: the only thing that reveals them on touch is opacity 0.5.
FLIP_OLD = ".flip-zone:not([disabled]) { opacity: 0.5; }"
FLIP_NEW = ".flip-zone:not([disabled]) { opacity: 0; }"

# 2. nav-center: prevent the page counter wrapping; tighten spacing on mobile.
NAV_OLD = """.nav-center {
  font-family: var(--font-ui);
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--ink-light);
  letter-spacing: 0.14em;
}"""
NAV_NEW = """.nav-center {
  font-family: var(--font-ui);
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--ink-light);
  letter-spacing: 0.14em;
  white-space: nowrap;
}
@media (max-width: 640px) {
  .nav-center { letter-spacing: 0.06em; }
}"""

readers = sorted(LIB.glob("reader-*.html"))
if not readers:
    sys.exit("no reader files found")

failures = []
for f in readers:
    text = f.read_text(encoding="utf-8")
    orig = text
    n_flip = text.count(FLIP_OLD)
    n_nav = text.count(NAV_OLD)
    if n_flip != 1 or n_nav != 1:
        failures.append(f"{f.name}: flip={n_flip} nav={n_nav}")
        continue
    text = text.replace(FLIP_OLD, FLIP_NEW)
    text = text.replace(NAV_OLD, NAV_NEW)
    if text != orig:
        f.write_text(text, encoding="utf-8")
    print(f"patched {f.name}")

if failures:
    sys.exit("UNEXPECTED MATCH COUNTS:\n" + "\n".join(failures))
print(f"\nDone: {len(readers)} readers patched.")
