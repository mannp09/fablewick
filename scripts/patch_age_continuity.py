#!/usr/bin/env python3
"""Age-range continuity + mobile hover-button fixes.

1. meta.json is canonical. kitchen-of-love is bumped to 5-9 (to match soil) per request.
2. Landing-page age badges aligned to each book's meta.json value.
3. kitchen reader cover tagline + all i18n cover translations -> 5-9.
4. Hide the hover-only ↗ card button on touch devices (mobile).
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIB = ROOT / "library"
BOOKS = ROOT / "src" / "content" / "books"

def edit(path, old, new, expect=1):
    text = path.read_text(encoding="utf-8")
    n = text.count(old)
    if n != expect:
        sys.exit(f"{path.name}: expected {expect} of {old!r}, found {n}")
    path.write_text(text.replace(old, new), encoding="utf-8")
    print(f"  {path.name}: {old!r} -> {new!r} x{n}")

# ── 1. kitchen-of-love meta -> [5, 9] ───────────────────────────
print("meta.json:")
kmeta = BOOKS / "kitchen-of-love" / "meta.json"
d = json.loads(kmeta.read_text(encoding="utf-8"))
assert d["ageRange"] == [4, 8], d["ageRange"]
d["ageRange"] = [5, 9]
kmeta.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("  kitchen-of-love ageRange [4,8] -> [5,9]")

# Canonical age per slug (kitchen already bumped above)
AGES = {b.name: json.loads((b / "meta.json").read_text())["ageRange"] for b in BOOKS.iterdir() if b.is_dir()}

# ── 2. Landing badges aligned to meta (ASCII hyphen) ────────────
print("landing badges:")
landing = LIB / "fablewick-landing.html"
ltext = landing.read_text(encoding="utf-8")
for slug, (lo, hi) in AGES.items():
    want = f"{lo}-{hi}"
    pat = re.compile(r'(slug:\s*"' + re.escape(slug) + r'",\s*\n\s*age:\s*")([0-9]+-[0-9]+)(")')
    def repl(m, want=want, slug=slug):
        if m.group(2) != want:
            print(f"  {slug}: {m.group(2)} -> {want}")
        return m.group(1) + want + m.group(3)
    ltext, n = pat.subn(repl, ltext)
    if n != 1:
        sys.exit(f"landing: slug {slug} age line matched {n} times")
landing.write_text(ltext, encoding="utf-8")

# ── 3. kitchen reader tagline + i18n covers -> 5-9 (en-dash) ────
print("kitchen tagline/i18n:")
edit(LIB / "reader-kitchen-of-love.html", "ages 5–8", "ages 5–9", expect=1)
edit(LIB / "reader-kitchen-of-love.i18n.json", "5–8", "5–9", expect=5)

# ── 4. Hide hover ↗ button on touch (mobile) ───────────────────
print("hover button:")
btn_old = """.book-card:hover .card-hero::after {
  opacity: 1;
  transform: translateY(0);
}"""
btn_new = """@media (hover: hover) {
  .book-card:hover .card-hero::after {
    opacity: 1;
    transform: translateY(0);
  }
}"""
edit(landing, btn_old, btn_new, expect=1)

print("\nDone.")
