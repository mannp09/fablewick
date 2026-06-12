#!/usr/bin/env python3
"""
patch_reader_cover.py — Fablewick reader cover + topbar redesign.

Per Mann (2026-06-12), across all 11 library readers (idempotent):
  1. Top bar center -> Fablewick WORDMARK (fablewick-logo.png, full spelling),
     truly centered (absolute), ALWAYS English. Replaces the per-page title.
  2. Cover page (page 1): drop the redundant "FABLEWICK" kicker, move the
     title up, drop the story's cover.jpg art in below it, tagline beneath.
     Title + tagline still translate; art is language-independent.
  3. Left of the top bar keeps the flame mark (home) from patch_reader_nav.py.

Run:  python scripts/patch_reader_cover.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "library"
PAGES = ROOT / "src" / "assets" / "pages"

# applyLanguage: the topbar book-name translation is now dead (it's an image)
OLD_BOOKNAME_JS = (
    "  const bookName = document.querySelector('.book-topbar .book-name');\n"
    "  if (bookName && I18N.titles) bookName.textContent = I18N.titles[lang] || I18N.titles.en;"
)
NEW_BOOKNAME_JS = (
    "  // topbar shows the Fablewick wordmark (image) — always English, never translated"
)

TOPBAR_WORDMARK = (
    '<img class="topbar-wordmark" src="../src/assets/fablewick-logo.png" alt="Fablewick">'
)

CSS_BLOCK = """
/* ── COVER REDESIGN: centered wordmark + cover art ─────────────── */
.book-topbar .topbar-wordmark {
  position: absolute;
  left: 50%; top: 50%;
  transform: translate(-50%, -50%);
  height: 26px; width: auto; display: block;
  pointer-events: none;
}
@media (max-width: 560px) {
  .book-topbar .topbar-wordmark { height: 22px; }
}
.cover-page .page-inner {
  justify-content: flex-start;
  padding-top: 3vh;
  gap: 1.5rem;
}
.cover-art {
  width: 100%;
  max-width: 560px;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-cozy);
  overflow: hidden;
  background: var(--cream-dark);
  box-shadow: 0 10px 36px rgba(42, 33, 24, 0.14);
}
.cover-art img { width: 100%; height: 100%; object-fit: cover; display: block; }
@media (max-width: 600px) {
  .cover-title { font-size: clamp(2rem, 9vw, 2.8rem); }
  .cover-art { max-width: 100%; }
  .cover-page .page-inner { padding-top: 2vh; }
}
"""


def patch(path: Path) -> str:
    slug = path.stem[len("reader-"):]
    cover = PAGES / slug / "cover.jpg"
    if not cover.exists():
        raise RuntimeError(f"{path.name}: missing cover art {cover}")

    text = path.read_text(encoding="utf-8")
    if "topbar-wordmark" in text:
        return "skip (already patched)"

    # 1. topbar book title -> centered wordmark
    text, n = re.subn(r'<div class="book-name">[^<]*</div>', TOPBAR_WORDMARK, text, count=1)
    if n != 1:
        raise RuntimeError(f"{path.name}: book-name div not found (n={n})")

    # 2. cover block: drop kicker, insert art after the title
    repl = (
        r'\1\n'
        r'      <div class="cover-art"><img src="../src/assets/pages/'
        + slug + r'/cover.jpg" alt=""></div>'
    )
    text, n = re.subn(
        r'<div class="cover-kicker">[^<]*</div>\s*(<h1 class="cover-title">[^<]*</h1>)',
        repl, text, count=1,
    )
    if n != 1:
        raise RuntimeError(f"{path.name}: cover-kicker/title block not found (n={n})")

    # 3. dead applyLanguage book-name lines
    if OLD_BOOKNAME_JS not in text:
        raise RuntimeError(f"{path.name}: applyLanguage book-name lines not found")
    text = text.replace(OLD_BOOKNAME_JS, NEW_BOOKNAME_JS, 1)

    # 4. CSS
    if "COVER REDESIGN" not in text:
        text = text.replace("</style>", CSS_BLOCK + "</style>", 1)

    path.write_text(text, encoding="utf-8")
    return "patched"


def main():
    print("Fablewick reader cover redesign")
    readers = sorted(LIB.glob("reader-*.html"))
    if not readers:
        sys.exit(f"ERROR: no readers in {LIB}")
    for r in readers:
        print(f"  {r.name:48s} {patch(r)}")
    print("Done.")


if __name__ == "__main__":
    main()
