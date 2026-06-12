# Fablewick — Illustration Continuity Protocol

*Created 2026-06-10 from a visual audit of the 5 Kitchen of Love pages + 4 hero images. This file is the single source of truth for image style and character continuity. `character-reference.md` holds the per-character blocks; this file holds the rules.*

---

## 1. STYLE ANCHOR

Paste this paragraph **verbatim, unedited, identical** into EVERY image prompt across ALL books. It is the codified "Kitchen of Love look" (derived from kitchen-of-love-page-01 / page-07 and the four strongest heroes, not invented).

```
Hand-painted children's storybook illustration in traditional watercolor with fine sepia-brown ink linework: delicate contour lines on figures and focal objects, looser granulating washes in backgrounds, visible paper grain, and soft deckled watercolor edges fading into a warm cream paper margin. Soft diffused golden daylight from a single source. Palette of warm cream, ochre, amber, terracotta, sage green, and dusty rose. Gentle, warmly realistic proportions -- storybook-soft, never cartoonish, never photo-real, never flat digital. No text or lettering anywhere in the image. 16:9 aspect ratio.
```

What the anchor encodes (for human reference, not for pasting):

| Axis | Canon |
|---|---|
| Medium | Traditional watercolor + fine ink/pencil contour line |
| Linework | Sepia-brown, tight on focal subjects, dissolving in backgrounds |
| Edges | Deckled/soft watercolor borders fading into cream paper margin |
| Texture | Visible paper grain, granulating washes |
| Light | One soft golden source (window/sun), no hard shadows |
| Palette | Cream, ochre, amber, terracotta, sage, dusty rose; one accent color per scene |
| Proportions | Warmly realistic; NOT cartoon (the page-09 failure mode), NOT photo-real |
| Composition | Full storytelling environments, characters mid-action, props carry narrative |

## 2. Character lock rule

- Every recurring character gets ONE canonical block in `character-reference.md`: face, hair, clothing + exact colors, jewelry, build.
- That block is pasted **VERBATIM** into every prompt the character appears in. Never paraphrase, never trim.
- **Clothing never changes within a book.** Same sari, same kurta, same suit, same colors, page 1 through page 5. (Sari-color drift across the kitchen pages is the precedent this rule exists to kill.)
- Block order inside a prompt: STYLE ANCHOR first, character block(s) second, scene third, reference-image line, negative line.
- If a character has no block yet, author it in the book's prompt file from the approved page-01 / hero render, then copy it into `character-reference.md`.

## 3. Generation workflow (tool-agnostic: SuperGrok / Grok Imagine now, Higgsfield / Midjourney later)

```
per book:
  1. Generate page-01 with: STYLE ANCHOR + character block(s) + scene + negative line.
  2. STOP. Mann approves page-01. Once approved it is the book's VISUAL ANCHOR.
  3. Pages 02-05: attach/reference the approved page-01 image
     + paste the page prompt (same anchor, same verbatim blocks, new scene)
     + the line "Match the attached reference image exactly for character
       appearance and art style."
  4. ONE page at a time. Inspect before generating the next.
  5. Quality mode ONLY. Never accept a Speed-mode fallback
     (kitchen-of-love page-09 is the precedent: Speed fallback = style break).
```

Reject-and-regen criteria (any one = reject):

```
[x] Face changed (age, nose, eyes, expression baseline)
[x] Clothing or clothing color shifted from the canonical block
[x] Style flattened (cartoon outlines, flat digital shading, lost paper texture)
[x] Extra fingers / malformed hands
[x] Any text, lettering, or word-like artifacts in the image
```

## 4. Drift log — audit of 2026-06-10

### Kitchen of Love (5 pages + hero)

| Image | Verdict | Drift found |
|---|---|---|
| page-01 | CANON BASELINE | Cream floral sari w/ maroon border, low silver bun, gold bangle. Minor: bindi not visible (canon block includes it). |
| page-03 | OK | Food still life, no characters. Style on-canon. |
| page-05 | DRIFT | Sari shifted to pale pink; pallu drawn OVER Ba's head (only page where head is covered); rendering softer/pastel, ink line nearly gone. Grandchild wears ochre t-shirt (vs. yellow kurta in hero/p09). |
| page-07 | DRIFT | Sari shifted to dusty rose with large multicolor floral pallu + clearly visible pink blouse; heavier painterly pigment; Ba reads younger/slimmer; ring + extra bangles appear. |
| page-09 | STYLE BREAK | Speed-mode fallback. Full cartoon: bold outlines, exaggerated nose/brows, flat shading, empty background. Ba in magenta blouse, elongated red bindi, green bangles, voluminous half-up hair. **Regen pending** -- prompt ready at `page-prompts/kitchen-of-love.md`. |
| hero | NEAR-CANON | Closest to page-01. Unique extras: red flower in hair, gold necklace (appear nowhere else). |

Net: **no two kitchen pages with people share the same sari.** Cream (p01) -> pink (p05) -> rose (p07) -> cream/magenta-blouse (p09). The canonical sari is now locked: cream-blush base, small dusty-pink-and-sage floret print, thin maroon border (per page-01 + hero).

### Hero spread vs. kitchen canon

| Hero | Style vs. canon | Character notes |
|---|---|---|
| hero-the-quiet-bear | ON CANON | Watercolor + ink, sage/amber, deckled edge. Matches Wren/Bear blocks. |
| hero-hands-in-the-soil | ON CANON | Strong linework, terracotta/sage. BUT: Dada has a gray mustache + short beard (absent from his block -- block amended 2026-06-10); the child is a GIRL in yellow kurta with braids + red bows, while the page prompts say "child ~7 in t-shirt and shorts." **Needs Mann's call before generating pages.** |
| hero-the-girl-who-stopped-looking | MOSTLY ON CANON (slightly cleaner/saturated edge) | CONTRADICTS Maya's block: hero shows teal star-print swim cap + teal suit, dark curly hair, deeper skin tone; block says long braid, purple hair tie, purple suit, no cap. Page prompts follow the purple block -> pages will not match the hero. **Needs Mann's call: regen hero, or amend Maya's block to teal-cap canon.** |
| hero-kitchen-of-love | ON CANON | Reference-grade for the whole site style. |

## 5. Known open items

| # | Item | Status |
|---|---|---|
| 1 | Kitchen page-09 hug regen (Speed-mode break, filed 2026-05-27) | Prompt ready: `page-prompts/kitchen-of-love.md`. Quality mode, attach page-01 as reference. |
| 2 | Maya hero vs. block contradiction | Awaiting Mann: pick teal-cap hero canon or purple-braid block canon. |
| 3 | Hands-in-the-Soil child: girl-in-kurta (hero) vs. t-shirt child (prompts) | Awaiting Mann. |
| 4 | Kitchen p05/p07 sari drift | Tolerated for now (pages live); any future kitchen regen uses the locked cream-blush sari block. |

*Last updated: 2026-06-10*

---

## 6. Amendment — 2026-06-11: full library regenerated on Gemini (Nano Banana Pro)

- **Stack switch ratified:** SuperGrok → **Gemini Plus (web app, Pro / Nano Banana)** per the 6/10 stack comparison; Mann bought Gemini Plus and gave autonomous go ("finish fablewick... utilize gemini for pictures - and continuity").
- **All 11 books rebuilt fresh: 11 covers + 55 interior pages (66 images)** at 2752×1536 PNG, no watermark, filed to `src/assets/pages/<slug>/` (+ web JPGs). Heroes in `src/assets/heroes/` overwritten with the new covers; all 11 reader HTMLs rewired to per-page art (no more repeated-hero placeholders). Kitchen p09 Speed-mode break (open since 5/27): **closed** — whole book regenerated on-canon.
- **Method that held continuity:** one chat per book; STYLE ANCHOR + verbatim character block in message 1 with the cover; pages as "Approved. Create an image - PAGE N: <scene>. Same characters, same style." In-session memory held characters with zero re-uploads. Full prompt log: `gemini-prompts/`.
- **Canon calls made autonomously (all-new covers mooted the old hero conflicts):** Maya = the BLOCK (purple braid + purple suit, no cap) + new Coach Ngu block live; Hands child = page-prompts version (boy ~7, cream t-shirt + brown shorts); Dada = block (no beard); Ba canon held incl. bindi; Pip's cloud gained a gentle face (adopted mid-book); open items #1-#4 in §5: **all closed**.
- **Gemini gotchas (for next run):** start prompts with "Create an image:" or Pro may answer in text and hallucinate a render; send via DOM injection (keyboard send is flaky); streams wedge on "Stop response" → reload; **chat history does not persist** (Apps Activity off) — download immediately, wait ≥10s before navigating; ~50-60 Pro images/day then silent downgrade to Flash-Lite (still usable).

*Last updated: 2026-06-11*

## 6. Text rewrite — 2026-06-12

All 11 books rewritten for read-aloud flow (3 levels each, Fablewick voice; "Something to think about" codas removed library-wide). Readers carry the new English via `scripts/inject_reader_text.py`. **Known drift:** reader translations (hi/gu/es/fr) still translate the pre-polish English — same story, older phrasing. Regenerate via `translations/build_translations.py` when next touched.
