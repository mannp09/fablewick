"""Inject rewritten story text into the Fablewick readers.

Source: _rewrite/<slug>.pages.json  (array of exactly 5 page strings, \n\n paragraphs)
Targets, per book:
  library/reader-<slug>.html
    - the 5 <div class="page-text">...</div> blocks (English markup)
    - the inlined `const I18N = {...};` JSON blob -> pageTexts.en
  library/reader-<slug>.i18n.json -> pageTexts.en

Other languages (hi/gu/es/fr) are left as-is: they still tell the same story;
they translate the pre-polish English. Flagged in docs/continuity-protocol.md.

Run from anywhere:  python 1-Projects/fablewick/scripts/inject_reader_text.py
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

FAB = Path(__file__).resolve().parents[1]
REWRITE = FAB / "_rewrite"
LIB = FAB / "library"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def page_html(text: str) -> str:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    inner = "\n".join(f"        <p>{esc(p)}</p>" for p in paras)
    return f'<div class="page-text">\n{inner}\n      </div>'


def main() -> int:
    sidecars = sorted(REWRITE.glob("*.pages.json"))
    if not sidecars:
        print("no _rewrite/*.pages.json found")
        return 1
    failures = 0
    for pj in sidecars:
        slug = pj.name.replace(".pages.json", "")
        pages = json.loads(pj.read_text(encoding="utf-8"))
        if not (isinstance(pages, list) and len(pages) == 5 and all(isinstance(p, str) and p.strip() for p in pages)):
            print(f"✗ {slug}: sidecar is not 5 non-empty strings")
            failures += 1
            continue

        reader = LIB / f"reader-{slug}.html"
        if not reader.exists():
            print(f"✗ {slug}: no reader html")
            failures += 1
            continue
        html = reader.read_text(encoding="utf-8")

        # 1. replace the 5 page-text divs in order
        blocks = list(re.finditer(r'<div class="page-text">.*?</div>', html, re.S))
        if len(blocks) != 5:
            print(f"✗ {slug}: found {len(blocks)} page-text divs, expected 5 — skipped")
            failures += 1
            continue
        out, last = [], 0
        for m, text in zip(blocks, pages):
            out.append(html[last:m.start()])
            out.append(page_html(text))
            last = m.end()
        out.append(html[last:])
        html = "".join(out)

        # 2. replace pageTexts.en inside the inlined I18N blob
        m = re.search(r"const I18N = (\{.*?\});\n", html, re.S)
        if not m:
            print(f"✗ {slug}: inlined I18N blob not found — skipped")
            failures += 1
            continue
        i18n = json.loads(m.group(1))
        i18n["pageTexts"]["en"] = pages
        html = html[: m.start(1)] + json.dumps(i18n, ensure_ascii=False) + html[m.end(1):]

        reader.write_text(html, encoding="utf-8")

        # 3. sidecar i18n json
        sc = LIB / f"reader-{slug}.i18n.json"
        if sc.exists():
            j = json.loads(sc.read_text(encoding="utf-8"))
            j["pageTexts"]["en"] = pages
            sc.write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"✓ {slug}: 5 pages injected (html + inline i18n + sidecar)")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
