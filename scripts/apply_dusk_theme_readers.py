#!/usr/bin/env python3
"""
apply_dusk_theme_readers.py — extend the approved dusk-glow night sky +
twinkling starfield to all 11 readers, exact-matching the landing.

Per Mann: "I want the home page twinkle and gradient to be exact for all pages."

Each reader gets (idempotent, marker "DUSK THEME (reader)"):
  - body bg -> dusk-glow gradient (navy -> plum -> warm horizon), fixed
  - #starfield: fixed twinkling 4-point starfield behind content, reduced-motion safe
  - chrome re-themed for dark: topbar, progress, nav-bar, buttons, dots -> light
  - story text, cover title/tagline, end text flipped to light so they stay readable
  - illustrations untouched; flame mark + Read buttons already work on dark

Run:  python scripts/apply_dusk_theme_readers.py
"""
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "library"

DUSK_CSS = """
/* ── DUSK THEME (reader) — night sky + light text/chrome ─────── */
body { background: linear-gradient(180deg, #1C2A52 0%, #46396A 52%, #B97E7A 100%) !important; background-attachment: fixed !important; }
#starfield { position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
#starfield .twk { position: absolute; opacity: 0.16; will-change: opacity, transform; }
@keyframes fwTw { 0%,40%,100% { opacity: 0.14; transform: scale(0.6); } 47% { opacity: 1; transform: scale(1); } 54% { opacity: 0.14; transform: scale(0.6); } }
@media (prefers-reduced-motion: reduce) { #starfield .twk { animation: none !important; opacity: 0.5 !important; } }

.stage { z-index: 1; }
.book-topbar { background: rgba(24, 34, 66, 0.74) !important; border-bottom-color: rgba(255,255,255,0.12) !important; }
.book-topbar .back-link .back-label { color: #E7DFF3 !important; }
.page-counter { color: #CFC6DD !important; }
.progress-track { background: rgba(255,255,255,0.10) !important; }

.page-text, .page-text p { color: #EFE7DD !important; }
.cover-title { color: #FBF4EC !important; }
.cover-tagline { color: #E6DAE4 !important; }
.cover-kicker { color: #E9BD93 !important; }
.end-mark { color: #E9BD93 !important; }
.end-line { color: #E6DAE4 !important; }

.nav-bar { background: rgba(24, 34, 66, 0.78) !important; border-top-color: rgba(255,255,255,0.12) !important; }
.nav-btn.prev { background: rgba(255,255,255,0.12) !important; color: #EADFF0 !important; }
.nav-btn.next { background: #F3ECE2 !important; color: #2A2342 !important; }
.nav-center { color: #CFC6DD !important; }
.nav-center .dot { background: rgba(255,255,255,0.28) !important; }
.nav-center .dot.active { background: #E9BD93 !important; }
"""

STARFIELD_DIV = '<body>\n<div id="starfield" aria-hidden="true"></div>'

STAR_JS = """
// ─── DUSK THEME starfield (reader) ────────────────────────────
(function () {
  var sky = document.getElementById('starfield');
  if (!sky) return;
  var spark = '<svg viewBox="0 0 24 24" width="100%" height="100%" aria-hidden="true"><path d="M12 0 L13.5 10.5 L24 12 L13.5 13.5 L12 24 L10.5 13.5 L0 12 L10.5 10.5 Z" fill="#FFF6E0"/></svg>';
  var n = Math.max(30, Math.min(80, Math.round(window.innerWidth * window.innerHeight / 16000)));
  for (var i = 0; i < n; i++) {
    var s = document.createElement('div');
    s.className = 'twk';
    var size = (3 + Math.random() * 6).toFixed(1);
    s.style.left = (Math.random() * 99).toFixed(1) + '%';
    s.style.top = (Math.random() * 92).toFixed(1) + '%';
    s.style.width = size + 'px';
    s.style.height = size + 'px';
    s.style.animation = 'fwTw ' + (2.4 + Math.random() * 3.2).toFixed(2) + 's ease-in-out ' + (Math.random() * 6).toFixed(2) + 's infinite';
    s.innerHTML = spark;
    sky.appendChild(s);
  }
})();
"""


def patch(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if "DUSK THEME (reader)" in text:
        return "skip (already themed)"
    if "</style>" not in text or "<body>" not in text:
        raise RuntimeError(f"{path.name}: missing </style> or <body>")
    text = text.replace("</style>", DUSK_CSS + "</style>", 1)
    text = text.replace("<body>", STARFIELD_DIV, 1)
    idx = text.rfind("</script>")
    if idx == -1:
        raise RuntimeError(f"{path.name}: no </script>")
    text = text[:idx] + STAR_JS + text[idx:]
    path.write_text(text, encoding="utf-8")
    return "themed"


def main():
    readers = sorted(LIB.glob("reader-*.html"))
    if not readers:
        sys.exit(f"ERROR: no readers in {LIB}")
    print("Dusk theme -> readers")
    for r in readers:
        print(f"  {r.name:48s} {patch(r)}")
    print("Done.")


if __name__ == "__main__":
    main()
