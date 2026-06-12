#!/usr/bin/env python3
"""
patch_reader_nav.py — Fablewick reader nav upgrade.

Applies three changes to all 11 library readers (idempotent, re-runnable):
  1. Top-left back-link -> flame-book brand mark (image) + "Library" label,
     still linking home. i18n hook retargeted to the .back-label span so it
     no longer wipes the <img> via textContent.
  2. Click-to-flip side gutters (left = prev, right = next), wired to goTo().
     Existing buttons / dots / arrow keys keep working unchanged.
  3. goTo() upgraded from a slide to a 3D leaf page-turn (pure CSS/JS, no lib;
     prefers-reduced-motion falls back to a clean fade).

Also copies the chosen logo contender -> src/assets/fablewick-mark.png once.

Run from anywhere:  python scripts/patch_reader_nav.py
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # 1-Projects/fablewick
LIB = ROOT / "library"
ASSETS = ROOT / "src" / "assets"
MARK_SRC = ASSETS / "logo-contenders" / "contender-1-book-flame-transparent.png"
MARK_DST = ASSETS / "fablewick-mark.png"

# ── replacements (exact strings; all 11 readers share one template) ──────────

OLD_BACKLINK = '<a href="fablewick-landing.html" class="back-link">← Library</a>'
NEW_BACKLINK = (
    '<a href="fablewick-landing.html" class="back-link" aria-label="Fablewick home">'
    '<img class="brand-mark" src="../src/assets/fablewick-mark.png" alt="Fablewick">'
    '<span class="back-label">Library</span></a>'
)

OLD_APPLYLANG = (
    "  const backLink = document.querySelector('.book-topbar .back-link');\n"
    "  if (backLink) backLink.textContent = I18N.back_labels[lang] || I18N.back_labels.en;"
)
NEW_APPLYLANG = (
    "  const backLabel = document.querySelector('.book-topbar .back-link .back-label');\n"
    "  if (backLabel) backLabel.textContent = (I18N.back_labels[lang] || I18N.back_labels.en).replace(/^[←\\s]+/, '');"
)

OLD_STAGE = '<div class="stage" id="stage" role="main">'
NEW_STAGE = (
    '<div class="stage" id="stage" role="main">\n'
    '  <button class="flip-zone flip-prev" id="flipPrev" type="button" aria-label="Previous page" tabindex="-1"></button>\n'
    '  <button class="flip-zone flip-next" id="flipNext" type="button" aria-label="Next page" tabindex="-1"></button>'
)

OLD_NEXTCONST = "const nextBtn = document.getElementById('nextBtn');"
NEW_NEXTCONST = (
    "const nextBtn = document.getElementById('nextBtn');\n"
    "const flipPrev = document.getElementById('flipPrev');\n"
    "const flipNext = document.getElementById('flipNext');"
)

OLD_LISTENERS = (
    "prevBtn.addEventListener('click', () => goTo(currentIdx - 1));\n"
    "nextBtn.addEventListener('click', () => goTo(currentIdx + 1));"
)
NEW_LISTENERS = (
    "prevBtn.addEventListener('click', () => goTo(currentIdx - 1));\n"
    "nextBtn.addEventListener('click', () => goTo(currentIdx + 1));\n"
    "if (flipPrev) flipPrev.addEventListener('click', () => goTo(currentIdx - 1));\n"
    "if (flipNext) flipNext.addEventListener('click', () => goTo(currentIdx + 1));"
)

OLD_DISABLED = (
    "  prevBtn.disabled = currentIdx === 0;\n"
    "  nextBtn.disabled = currentIdx === total - 1;"
)
NEW_DISABLED = (
    "  prevBtn.disabled = currentIdx === 0;\n"
    "  nextBtn.disabled = currentIdx === total - 1;\n"
    "  if (flipPrev) flipPrev.disabled = currentIdx === 0;\n"
    "  if (flipNext) flipNext.disabled = currentIdx === total - 1;"
)

OLD_GOTO = """function goTo(newIdx) {
  if (newIdx < 0 || newIdx >= total || newIdx === currentIdx) return;
  const dir = newIdx > currentIdx ? 1 : -1;
  const oldPage = pages[currentIdx];
  const newPage = pages[newIdx];
  if (dir > 0) {
    oldPage.classList.remove('active');
    oldPage.classList.add('exit-left');
  } else {
    oldPage.classList.remove('active');
  }
  setTimeout(() => {
    oldPage.classList.remove('exit-left');
    newPage.classList.add('active');
    // Scroll text panel to top
    const txt = newPage.querySelector('.page-text');
    if (txt) txt.scrollTop = 0;
  }, 50);

  currentIdx = newIdx;
  updateUI();
}"""

NEW_GOTO = """function goTo(newIdx) {
  if (newIdx < 0 || newIdx >= total || newIdx === currentIdx) return;
  const dir = newIdx > currentIdx ? 1 : -1;
  const oldPage = pages[currentIdx];
  const newPage = pages[newIdx];

  // incoming page: preset on the side it enters from (no transition for the preset)
  newPage.classList.remove('active', 'turn-fwd', 'turn-back', 'enter-fwd', 'enter-back');
  newPage.classList.add(dir > 0 ? 'enter-fwd' : 'enter-back');
  void newPage.offsetWidth;            // commit the preset before animating

  // outgoing page turns away like a leaf
  oldPage.classList.remove('active');
  oldPage.classList.add(dir > 0 ? 'turn-fwd' : 'turn-back');

  // incoming page settles flat
  newPage.classList.remove('enter-fwd', 'enter-back');
  newPage.classList.add('active');

  setTimeout(() => {
    oldPage.classList.remove('turn-fwd', 'turn-back', 'exit-left');
    const txt = newPage.querySelector('.page-text');
    if (txt) txt.scrollTop = 0;
  }, 600);

  currentIdx = newIdx;
  updateUI();
}"""

CSS_BLOCK = """
/* ── NAV UPGRADE: brand mark, flip zones, 3D page-turn ─────────── */
.book-topbar .back-link { display: inline-flex; align-items: center; gap: 0.5rem; }
.book-topbar .back-link .brand-mark {
  height: 30px; width: auto; display: block; object-fit: contain;
}
.book-topbar .back-link .back-label { line-height: 1; }
@media (max-width: 560px) {
  .book-topbar .back-link .back-label { display: none; }
  .book-topbar .back-link .brand-mark { height: 28px; }
}

/* Click-to-flip side gutters — over the page edges, clear of topbar + nav-bar */
.flip-zone {
  position: fixed;
  top: 58px;
  bottom: 4.75rem;
  width: 24%;
  max-width: 190px;
  z-index: 30;
  border: 0;
  background: transparent;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.25s ease;
}
.flip-prev { left: 0; justify-content: flex-start; padding-left: 0.4rem; }
.flip-next { right: 0; justify-content: flex-end; padding-right: 0.4rem; }
.flip-zone::before {
  font-family: var(--font-ui);
  font-size: 1.9rem;
  line-height: 1;
  color: var(--ink-light);
  width: 2.4rem; height: 2.4rem;
  display: flex; align-items: center; justify-content: center;
  background: rgba(251, 246, 238, 0.82);
  border-radius: 100px;
  box-shadow: 0 2px 10px rgba(42, 33, 24, 0.12);
}
.flip-prev::before { content: "\\2039"; }
.flip-next::before { content: "\\203A"; }
.flip-zone:hover, .flip-zone:focus-visible { opacity: 1; }
.flip-zone:focus { outline: none; }
.flip-zone[disabled] { opacity: 0 !important; pointer-events: none; }
@media (hover: none) {
  /* touch: show a faint resting hint so kids know the edges are tappable */
  .flip-zone:not([disabled]) { opacity: 0.5; }
}

/* 3D leaf page-turn (overrides the old slide; merges with the base .page rule) */
.stage { perspective: 2200px; }
.page {
  transform-origin: center center;
  transform: rotateY(0);
  transition: transform 0.6s cubic-bezier(0.22, 0.61, 0.21, 1), opacity 0.45s ease;
  backface-visibility: hidden;
}
.page.active { opacity: 1; pointer-events: auto; transform: rotateY(0) translateX(0); }
.page.enter-fwd  { transition: none; opacity: 0; transform-origin: right center; transform: rotateY(-15deg) translateX(7%); }
.page.enter-back { transition: none; opacity: 0; transform-origin: left center;  transform: rotateY(15deg)  translateX(-7%); }
.page.turn-fwd   { opacity: 0; transform-origin: left center;  transform: rotateY(36deg)  translateX(-4%); }
.page.turn-back  { opacity: 0; transform-origin: right center; transform: rotateY(-36deg) translateX(4%); }
.page::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  opacity: 0; transition: opacity 0.55s ease;
}
.page.turn-fwd::after  { opacity: 1; background: linear-gradient(90deg, rgba(42,33,24,0) 55%, rgba(42,33,24,0.16)); }
.page.turn-back::after { opacity: 1; background: linear-gradient(90deg, rgba(42,33,24,0.16), rgba(42,33,24,0) 45%); }

@media (prefers-reduced-motion: reduce) {
  .page, .page.active,
  .page.enter-fwd, .page.enter-back,
  .page.turn-fwd, .page.turn-back {
    transition: opacity 0.3s ease !important;
    transform: none !important;
  }
  .page::after { display: none !important; }
}
"""

REPLACEMENTS = [
    ("back-link markup", OLD_BACKLINK, NEW_BACKLINK),
    ("applyLanguage hook", OLD_APPLYLANG, NEW_APPLYLANG),
    ("stage flip zones", OLD_STAGE, NEW_STAGE),
    ("flip consts", OLD_NEXTCONST, NEW_NEXTCONST),
    ("flip listeners", OLD_LISTENERS, NEW_LISTENERS),
    ("updateUI disabled", OLD_DISABLED, NEW_DISABLED),
    ("goTo() page-turn", OLD_GOTO, NEW_GOTO),
]


def copy_mark():
    if not MARK_SRC.exists():
        sys.exit(f"ERROR: source mark not found: {MARK_SRC}")
    shutil.copyfile(MARK_SRC, MARK_DST)
    print(f"  asset: {MARK_SRC.name} -> {MARK_DST.relative_to(ROOT)}")


def patch_reader(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if "fablewick-mark.png" in text and "flip-zone" in text:
        return "skip (already patched)"

    for label, old, new in REPLACEMENTS:
        n = text.count(old)
        if n != 1:
            raise RuntimeError(f"{path.name}: '{label}' expected 1 match, found {n}")
        text = text.replace(old, new)

    # inject CSS once, just before the closing </style>
    if "NAV UPGRADE" not in text:
        if text.count("</style>") < 1:
            raise RuntimeError(f"{path.name}: no </style> to inject before")
        text = text.replace("</style>", CSS_BLOCK + "</style>", 1)

    path.write_text(text, encoding="utf-8")
    return "patched"


def main():
    print("Fablewick reader nav patch")
    copy_mark()
    readers = sorted(LIB.glob("reader-*.html"))
    if not readers:
        sys.exit(f"ERROR: no readers found in {LIB}")
    print(f"  readers: {len(readers)}")
    for r in readers:
        status = patch_reader(r)
        print(f"    {r.name:48s} {status}")
    print("Done.")


if __name__ == "__main__":
    main()
