# Fablewick — Character Reference Sheet

**Purpose:** Every illustration prompt for a recurring character must include the **identical** description from this file. Otherwise SuperGrok renders a different-looking person every time. Paste the relevant block VERBATIM into each prompt for that character's story.

---

## Ba — Gujarati grandmother (Kitchen of Love)

```
Ba: a Gujarati grandmother in her mid-60s, warm brown skin, kind round face with soft wrinkles around the eyes and a small smile-line at the mouth, silver-gray hair pulled back into a low neat bun (no loose front strands), wearing the same soft cotton sari with a delicate pink-and-cream floral pattern (small repeating florets, faded with age), simple gold stud earrings, small red bindi between her brows. She is the same person in every scene — same face, same hair, same sari, same posture.
```

**Style directive (shared with all Fablewick illustrations):**
```
Warm painterly children's book illustration, soft watercolor texture, gentle brushstrokes, imaginative not photo-rendered, room for the child's imagination, slightly textured paper background, no text or lettering, 16:9 aspect ratio.
```

---

## Dada — Gujarati grandfather (Hands in the Soil)

```
Dada: a Gujarati grandfather in his late-60s, warm brown skin, kind weathered face, receding hairline with short gray hair on the sides and back, deep laugh lines, wearing the same simple white cotton kurta over loose cotton pants, slightly stained at the knees from the garden, no glasses, no jewelry. He is the same person in every scene — same face, same hairline, same kurta, same gentle hands.
```

---

## Maya — Young swimmer (The Girl Who Stopped Looking)

```
Maya: a 9-year-old Indian-American girl with warm light-brown skin, long dark hair in a single braid with a purple hair tie, alert focused brown eyes, wearing the same purple one-piece swimsuit, no goggles, mid-stroke in a swimming pool. She is the same person in every scene — same face, same braid, same suit.
```

---

## Franklin — Young FDR (The Boy Who Couldn't Walk)

```
Franklin: a young boy around 10 years old (book-aged, not historical), light skin, reddish-brown short combed hair parted on the side, serious thoughtful expression, wearing the same dark-blue sailor-style sweater over a white collared shirt and knee shorts, sometimes a wicker wheelchair behind him. Same person across all scenes.
```

---

## Morgan — J.P. Morgan (The Stillest Man in the Room)

```
Morgan: an older man in his 60s, stout build, prominent nose, thick white mustache, slicked-back white hair, serious composed expression, wearing the same dark three-piece wool suit with a gold pocket watch chain across the vest, sitting or standing very still. Same person across all scenes.
```

---

## Animal characters (single appearance per book, less critical)

For Pip (field mouse), Moss (hedgehog), Tuli (red fox), Wren (small brown bird), Bear (large brown bear): describe consistently if multiple scenes are generated for the same book, but cross-book consistency isn't needed.

---

## How to apply

Every new Fablewick prompt for a recurring-character story should follow this template:

```
{STYLE DIRECTIVE}

{CHARACTER REFERENCE BLOCK}

Scene: {what's happening in this specific image — composition, setting, action, mood, palette}.
```

The character block goes BEFORE the scene description so SuperGrok anchors the character first. Repeat the entire block verbatim in every prompt for that character — don't paraphrase.

---

## Known continuity issue (filed 2026-05-27)

Mann flagged that the Kitchen of Love page-09 hug image differs in style from the other 4 (Speed-mode fallback after the daily Quality limit hit). Regenerate this image after the next Quality reset (6:20 AM) using the Ba reference block + the original page-09 prompt.

Also: pages 1, 3 (no people), 5, 7 of Kitchen of Love are reasonably consistent. Page 9 needs to match.

---

## Addendum — 2026-06-10 visual audit (supersedes blocks above where they conflict)

Full audit + drift log + workflow: `continuity-protocol.md`. The style directive above is **superseded** by the STYLE ANCHOR in that file (also baked into every `page-prompts/*.md`). Regen prompt for the page-09 hug: `page-prompts/kitchen-of-love.md`.

### Ba — audited canonical block (richer; from kitchen page-01 + hero)

```
Ba: a Gujarati grandmother in her late-60s, warm brown skin, kind round face with soft wrinkles around the eyes and a gentle closed-mouth smile, silver-gray hair center-parted and pulled back into a low neat bun (no loose front strands, nothing covering her head), small round red bindi, simple gold stud earrings, two thin gold bangles on her right wrist, medium build with a slight grandmotherly stoop. She wears the same soft cotton sari in every scene: cream-blush base with a small repeating dusty-pink-and-sage floret print and a thin maroon border, draped over her left shoulder, with a matching blush short-sleeved blouse. She is the same person in every scene — same face, same hair, same sari, same jewelry.
```

Pinned decisions: sari = cream-blush w/ maroon border (page-01 + hero pair; the pink/rose saris on pages 05/07 are drift); pallu never over her head (page-05 drift); the hero's red hair-flower and necklace are NOT canon (appear nowhere else).

### Grandchild (Kitchen of Love) — new block, pinned from hero

```
The grandchild: a boy around 5 years old, warm brown skin, round soft cheeks, big dark eyes, short tousled black hair, wearing the same mustard-yellow cotton kurta with simple stitching at the collar and white cotton pants. He is the same boy in every scene — same face, same hair, same kurta.
```

(Page-05's ochre t-shirt is drift; hero + page-09 agree on the yellow kurta.)

### Dada — addendum from `hero-hands-in-the-soil.jpg`

The hero clearly shows a **gray mustache + short gray beard** (absent from the block above). If the hero is canon, append to his block: "short neatly-trimmed gray mustache and beard". Also: the hero's child is a **girl** with two braids, red bows, mustard-yellow kurta top, green leggings — but the page prompts describe "a child around 7 in simple t-shirt and shorts." **NEEDS MANN: which child is canon before generating pages.**

### Maya — CONFLICT between hero and block

`hero-the-girl-who-stopped-looking.jpg` shows: deeper brown skin, dark curly hair gathered under a **teal star-print swim cap**, **teal swimsuit** — vs. the block above (long braid, purple hair tie, purple suit, no cap). Page prompts currently follow the purple block, so generated pages will not match the live hero. **NEEDS MANN: regen the hero to the purple block, or re-canon Maya to the teal-cap look (then update the block + 5 page prompts).**

*Addendum last updated: 2026-06-10*
