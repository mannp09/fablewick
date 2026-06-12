#!/usr/bin/env python3
"""
fix_translations.py — transliterate names + translate "Bear" + transliterate
Tuli's whistle sounds inside the Hindi/Gujarati translations (Mann's calls).

  - Landing hi/gu strings: names -> Devanagari/Gujarati (Bear -> animal noun)
  - kitchen-of-love sidecar: re-synced from its already-correct inline
  - tulis-whistle: whistle sounds transliterated in sidecar + inline (hi+gu)
  - es/fr: untouched (Latin proper nouns are correct there)
  - meta.json: English-only, nothing to do

Run:  python scripts/fix_translations.py
"""
import json, re
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "library"
INLINE = re.compile(r"const I18N = (\{.*?\});", re.DOTALL)

NAMES = {
    "hi": {"J.P.": "जे.पी.", "Ba": "बा", "Dada": "दादा", "Pip": "पिप", "Moss": "मॉस",
           "Tuli": "तुली", "Maya": "माया", "Wren": "रेन", "Franklin": "फ़्रैंकलिन",
           "Morgan": "मॉर्गन", "Bear": "भालू"},
    "gu": {"J.P.": "જે.પી.", "Ba": "બા", "Dada": "દાદા", "Pip": "પિપ", "Moss": "મૉસ",
           "Tuli": "તુલી", "Maya": "માયા", "Wren": "રેન", "Franklin": "ફ્રેન્કલિન",
           "Morgan": "મૉર્ગન", "Bear": "રીંછ"},
}
# longest-first so e.g. PFFFFFF is consumed before Pff
SOUNDS = {
    "hi": [("PFFFFFFFFFFFF", "प्फ़्फ़्फ़्फ़्फ़्फ़"), ("PFFFFFF", "प्फ़्फ़्फ़्फ़"),
           ("PFEEEE", "प्फ़ीईईई"), ("Pffffff", "प्फ़्फ़्फ़"), ("Pfff", "प्फ़्फ़"),
           ("Pff", "प्फ़")],
    "gu": [("PFFFFFFFFFFFF", "પ્ફ્ફ્ફ્ફ્ફ્ફ"), ("PFFFFFF", "પ્ફ્ફ્ફ્ફ"),
           ("PFEEEE", "પ્ફીઈઈઈ"), ("Pffffff", "પ્ફ્ફ્ફ"), ("Pfff", "પ્ફ્ફ"),
           ("Pff", "પ્ફ")],
}
O_SHAPE = {"hi": "ओ", "gu": "ઓ"}


def repl_names(text, lang):
    for name, script in NAMES[lang].items():
        text = re.sub(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])", script, text)
    return text


def repl_sounds(text, lang):
    for tok, script in SOUNDS[lang]:
        text = text.replace(tok, script)
    text = re.sub(r"(?<![A-Za-z])O(?![A-Za-z])", O_SHAPE[lang], text)
    return text


def read_inline(html):
    m = INLINE.search(html)
    return m.group(0), json.loads(m.group(1))


def write_inline(html, old_blob, obj):
    return html.replace(old_blob, "const I18N = " + json.dumps(obj, ensure_ascii=False) + ";", 1)


# ── 1. LANDING: names in every hi/gu string ──────────────────────
land_path = LIB / "fablewick-landing.html"
land = land_path.read_text(encoding="utf-8")
counts = {"hi": 0, "gu": 0}

def land_cb(m):
    prefix, lang, inner, q = m.group(1), m.group(2), m.group(3), m.group(4)
    before = inner
    inner = repl_names(inner, lang)
    if inner != before:
        counts[lang] += 1
    return prefix + inner + q

land = re.sub(r'((hi|gu):\s*")((?:[^"\\]|\\.)*)(")', land_cb, land)
land_path.write_text(land, encoding="utf-8")
print(f"landing: name fixes applied in hi:{counts['hi']} strings, gu:{counts['gu']} strings")

# ── 2. kitchen-of-love sidecar <- inline (resync the romanized sidecar) ──
k_html = (LIB / "reader-kitchen-of-love.html").read_text(encoding="utf-8")
_, k_inline = read_inline(k_html)
(LIB / "reader-kitchen-of-love.i18n.json").write_text(
    json.dumps(k_inline, ensure_ascii=False, indent=2), encoding="utf-8")
print("kitchen-of-love: sidecar re-synced from inline (Ba/mango/guava/papaya now match the rendered text)")

# ── 3. tulis-whistle: transliterate sounds in sidecar, then set inline = sidecar ──
t_side = LIB / "reader-tulis-whistle.i18n.json"
t = json.loads(t_side.read_text(encoding="utf-8"))
for lang in ("hi", "gu"):
    t["pageTexts"][lang] = [repl_sounds(s, lang) for s in t["pageTexts"][lang]]
t_side.write_text(json.dumps(t, ensure_ascii=False, indent=2), encoding="utf-8")
t_html_path = LIB / "reader-tulis-whistle.html"
t_html = t_html_path.read_text(encoding="utf-8")
old_blob, _ = read_inline(t_html)
t_html = write_inline(t_html, old_blob, t)
t_html_path.write_text(t_html, encoding="utf-8")
print("tulis-whistle: whistle sounds transliterated in sidecar + inline (hi+gu)")

print("Done.")
