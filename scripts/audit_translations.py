#!/usr/bin/env python3
"""
audit_translations.py — find English/Latin text left inside non-English
translations (hi, gu primarily; es/fr Latin names noted separately).

Scans the reader sidecars (reader-*.i18n.json) AND the inline I18N in each
reader HTML, reporting every Latin-script token inside Hindi & Gujarati text
(names like Ba/Dada/Pip + leaked nouns like mango/guava), per book + global.
Also checks inline-vs-sidecar sync. READ-ONLY — changes nothing.

Run:  python scripts/audit_translations.py
"""
import json, re, collections
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "library"
LATIN = re.compile(r"[A-Za-z][A-Za-z'’.\-]*")
INLINE = re.compile(r"const I18N = (\{.*?\});", re.DOTALL)

gfreq_hi_gu = collections.Counter()
per_book = {}          # from sidecars
per_book_inline = {}   # from rendered inline I18N
sync_issues = []

def scan_fields(data, lang):
    toks = collections.Counter()
    for s in (data.get("pageTexts", {}).get(lang) or []):
        toks.update(LATIN.findall(s))
    for k in ("covers", "ends", "titles", "kickers"):
        v = data.get(k, {}).get(lang)
        if v:
            toks.update(LATIN.findall(v))
    return toks

for sidecar in sorted(LIB.glob("reader-*.i18n.json")):
    slug = sidecar.stem.replace(".i18n", "").replace("reader-", "")
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    book = {}
    for lang in ("hi", "gu"):
        toks = scan_fields(data, lang)
        if toks:
            book[lang] = toks
            gfreq_hi_gu.update(toks)
    per_book[slug] = book

    # inline-vs-sidecar sync check
    html = (LIB / f"reader-{slug}.html").read_text(encoding="utf-8")
    m = INLINE.search(html)
    if m:
        try:
            inline = json.loads(m.group(1))
            ibook = {}
            for lang in ("hi", "gu"):
                toks = scan_fields(inline, lang)
                if toks:
                    ibook[lang] = toks
            per_book_inline[slug] = ibook
            for lang in ("hi", "gu", "es", "fr"):
                sc = (data.get("pageTexts", {}).get(lang) or [])
                il = (inline.get("pageTexts", {}).get(lang) or [])
                if sc != il:
                    sync_issues.append(f"{slug}/{lang}: inline != sidecar")
        except Exception as e:
            sync_issues.append(f"{slug}: inline parse failed ({e})")
    else:
        sync_issues.append(f"{slug}: no inline I18N found")

print("=== Latin tokens inside HI / GU translations (per book) ===")
for slug, book in per_book.items():
    if any(book.values()):
        print(f"\n{slug}")
        for lang, toks in book.items():
            print(f"  {lang}: {sum(toks.values())} latin tokens -> {dict(toks.most_common())}")

print("\n=== GLOBAL Latin-token frequency across HI+GU (the things to translate) ===")
for tok, c in gfreq_hi_gu.most_common():
    print(f"  {tok:18s} {c}")

print("\n=== Latin tokens in RENDERED INLINE (what users actually see) ===")
for slug, book in per_book_inline.items():
    if any(book.values()):
        print(f"\n{slug}")
        for lang, toks in book.items():
            print(f"  {lang}: {sum(toks.values())} -> {dict(toks.most_common())}")
if not any(any(b.values()) for b in per_book_inline.values()):
    print("  (none — all rendered inline hi/gu is clean)")

print("\n=== inline-vs-sidecar sync ===")
print("\n".join(sync_issues) if sync_issues else "  all readers: inline == sidecar (in sync)")

# ── LANDING: scan hi/gu strings for Latin tokens (names in summaries/about) ──
print("\n=== LANDING (fablewick-landing.html) — Latin tokens in hi/gu strings ===")
land = (LIB / "fablewick-landing.html").read_text(encoding="utf-8")
land_freq = collections.Counter()
for lang in ("hi", "gu"):
    for m in re.finditer(rf'\b{lang}:\s*"((?:[^"\\]|\\.)*)"', land):
        land_freq.update(LATIN.findall(m.group(1)))
if land_freq:
    for tok, c in land_freq.most_common():
        print(f"  {tok:18s} {c}")
else:
    print("  (none found in extracted hi/gu strings)")
