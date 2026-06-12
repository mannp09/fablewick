#!/usr/bin/env python3
"""
apply_dusk_theme.py — wire the approved dusk-glow night sky + twinkling stars
into the real landing, and re-theme the page chrome light for the dark sky.

Operates on library/fablewick-landing.html. Idempotent (marker "DUSK THEME").

  - body bg -> dusk-glow gradient (navy -> plum -> warm horizon), fixed
  - #starfield: fixed full-screen layer of small 4-point stars, brief
    staggered twinkles, behind content, pointer-events none, reduced-motion safe
  - chrome (nav, hero subtitle, language pills, About card, footer) flipped to
    light tones so everything stays readable on dark; cards stay light and pop

Run:  python scripts/apply_dusk_theme.py
"""
import sys
from pathlib import Path

LANDING = Path(__file__).resolve().parent.parent / "library" / "fablewick-landing.html"

DARK_CSS = """
/* ── DUSK THEME — night sky background + light chrome ─────────── */
body {
  background: linear-gradient(180deg, #1C2A52 0%, #46396A 52%, #B97E7A 100%) !important;
  background-attachment: fixed !important;
  color: #F3ECE2;
}
#starfield { position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
#starfield .twk { position: absolute; opacity: 0.16; will-change: opacity, transform; }
@keyframes fwTw { 0%,40%,100% { opacity: 0.14; transform: scale(0.6); } 47% { opacity: 1; transform: scale(1); } 54% { opacity: 0.14; transform: scale(0.6); } }
@media (prefers-reduced-motion: reduce) { #starfield .twk { animation: none !important; opacity: 0.5 !important; } }

.top-nav, .site-header, .book-grid, .about-section, .site-footer { position: relative; z-index: 1; }

.top-nav { background: rgba(24, 34, 66, 0.74) !important; border-bottom-color: rgba(255,255,255,0.12) !important; }
.top-nav a.nav-link { color: #E7DFF3 !important; }
.top-nav a.nav-link:hover { color: #FFFFFF !important; border-bottom-color: #C9B6E0 !important; }

.site-subtitle { color: #E6DAE4 !important; }
.lang-btn { background: rgba(255,255,255,0.10) !important; color: #EADFF0 !important; border-color: rgba(255,255,255,0.22) !important; }
.lang-btn:hover { color: #FFFFFF !important; }
.lang-btn.active { background: #F3ECE2 !important; color: #2A2342 !important; border-color: #F3ECE2 !important; }

.about-section { background: rgba(24, 34, 66, 0.55) !important; border: 1px solid rgba(255,255,255,0.14) !important; }
.about-kicker { color: #DEB2A8 !important; }
.about-heading { color: #FBF4EC !important; }
.about-body { color: #E4D9DD !important; }
.about-rule { border-top-color: rgba(255,255,255,0.16) !important; }
.coauthor-label { color: #FBF4EC !important; }
.coauthor-body { color: #D6CBD2 !important; }
.author-link, .coauthor-label .author-link { color: #E9BD93 !important; }

.footer-main { color: #ECE2EA !important; }
.footer-sub { color: #CBBECC !important; }
.footer-sub span { color: #CBBECC !important; }
"""

STARFIELD_DIV = '<body>\n<div id="starfield" aria-hidden="true"></div>'

STAR_JS = """
// ─── DUSK THEME starfield — small twinkling 4-point stars ──────
(function () {
  var sky = document.getElementById('starfield');
  if (!sky) return;
  var spark = '<svg viewBox="0 0 24 24" width="100%" height="100%" aria-hidden="true"><path d="M12 0 L13.5 10.5 L24 12 L13.5 13.5 L12 24 L10.5 13.5 L0 12 L10.5 10.5 Z" fill="#FFF6E0"/></svg>';
  var n = Math.max(34, Math.min(90, Math.round(window.innerWidth * window.innerHeight / 15000)));
  for (var i = 0; i < n; i++) {
    var s = document.createElement('div');
    s.className = 'twk';
    var size = (3 + Math.random() * 6).toFixed(1);
    s.style.left = (Math.random() * 99).toFixed(1) + '%';
    s.style.top = (Math.random() * 90).toFixed(1) + '%';
    s.style.width = size + 'px';
    s.style.height = size + 'px';
    s.style.animation = 'fwTw ' + (2.4 + Math.random() * 3.2).toFixed(2) + 's ease-in-out ' + (Math.random() * 6).toFixed(2) + 's infinite';
    s.innerHTML = spark;
    sky.appendChild(s);
  }
})();
"""


def main():
    if not LANDING.exists():
        sys.exit(f"ERROR: {LANDING} not found")
    text = LANDING.read_text(encoding="utf-8")
    if "DUSK THEME" in text:
        print("skip (already themed)")
        return

    if "</style>" not in text:
        sys.exit("ERROR: no </style>")
    text = text.replace("</style>", DARK_CSS + "</style>", 1)

    if "<body>" not in text:
        sys.exit("ERROR: no <body>")
    text = text.replace("<body>", STARFIELD_DIV, 1)

    idx = text.rfind("</script>")
    if idx == -1:
        sys.exit("ERROR: no </script>")
    text = text[:idx] + STAR_JS + text[idx:]

    LANDING.write_text(text, encoding="utf-8")
    print("dusk theme applied -> fablewick-landing.html")


if __name__ == "__main__":
    main()
