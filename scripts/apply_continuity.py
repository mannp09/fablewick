#!/usr/bin/env python3
"""One-shot: bake the continuity protocol into all 10 page-prompt files.
- Replace old style directive with the new STYLE ANCHOR (inline, every prompt).
- Insert STYLE ANCHOR + workflow header at top of each file.
- After every Scene line: add reference-image line (anchor wording on page 1,
  match wording on pages 2-5) + negative line.
Idempotent-ish: skips files that already contain the anchor.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "page-prompts"

OLD_STYLE = ("Warm painterly children's book illustration, soft watercolor "
             "texture, gentle brushstrokes, imaginative not photo-rendered, "
             "room for the child's imagination, slightly textured paper "
             "background, no text or lettering, 16:9 aspect ratio.")

ANCHOR = ("Hand-painted children's storybook illustration in traditional "
          "watercolor with fine sepia-brown ink linework: delicate contour "
          "lines on figures and focal objects, looser granulating washes in "
          "backgrounds, visible paper grain, and soft deckled watercolor "
          "edges fading into a warm cream paper margin. Soft diffused golden "
          "daylight from a single source. Palette of warm cream, ochre, "
          "amber, terracotta, sage green, and dusty rose. Gentle, warmly "
          "realistic proportions -- storybook-soft, never cartoonish, never "
          "photo-real, never flat digital. No text or lettering anywhere in "
          "the image. 16:9 aspect ratio.")

NEG = ("Negative: no style drift from the watercolor-and-ink look, no "
       "clothing or color changes on any character, no text or words in the "
       "image, no extra fingers or malformed hands.")

REF_P1 = ("This image becomes the book's visual anchor: once approved, it is "
          "the reference image every later page in this book must match.")

REF_REST = ("Match the attached reference image exactly for character "
            "appearance and art style.")

HEADER = f"""
---

**STYLE ANCHOR — paste verbatim into every prompt below (identical across all Fablewick books; full rules: `../continuity-protocol.md`):**

```
{ANCHOR}
```

**Workflow (Quality mode ONLY — never Speed):** generate page 01 first → Mann approves it as this book's visual anchor → for pages 02-05, attach the approved page-01 image as the reference and paste the page prompt unchanged, one page at a time. Reject and regenerate if: face changed, clothing color shifted, style flattened/cartoonish, extra fingers, any text in the image.

---
"""

PAGE_RE = re.compile(r"^##\s*Page\s*(\d+)")

for path in sorted(ROOT.glob("*.md")):
    if path.name == "kitchen-of-love.md":
        continue
    text = path.read_text(encoding="utf-8")
    if ANCHOR in text:
        print(f"skip (already done): {path.name}")
        continue
    assert OLD_STYLE in text, f"old style line missing in {path.name}"
    text = text.replace(OLD_STYLE, ANCHOR)
    text = text.replace("Style directive", "Style anchor")

    lines = text.split("\n")
    out = []
    page = 0
    # insert header right after the H1 title line
    out.append(lines[0])
    out.append(HEADER.rstrip("\n"))
    for line in lines[1:]:
        m = PAGE_RE.match(line)
        if m:
            page = int(m.group(1))
        out.append(line)
        if line.startswith("Scene:") and page >= 1:
            ref = REF_P1 if page == 1 else REF_REST
            out.extend(["", ref, "", NEG])
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"updated: {path.name}")
