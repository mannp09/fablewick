# Contributing to Fablewick

The simplest, most valuable contribution is **a new story**. Here's how.

## Adding a book

Each book is a single folder under `src/content/books/` containing one file: `meta.json`.

### 1. Pick a slug

Use kebab-case based on the title: `the-quiet-bear`, `pip-and-the-lost-cloud`.

### 2. Create the folder and meta.json

```
src/content/books/your-book-slug/meta.json
```

Use this template (copy from any existing book to start):

```json
{
  "title": "Your Title",
  "author": "Your name or pen name",
  "ageRange": [4, 8],
  "themes": ["kindness", "nature", "..."],
  "lesson": "One sentence summarizing the lesson tucked inside — written for a reader, not a child.",
  "summary": "One-line summary shown on the library card.",
  "coverColor": "sage",
  "coverIllustration": "<svg viewBox='0 0 200 150' ...>...</svg>",
  "levels": {
    "1": { "label": "Little Listener", "wordCount": 180, "text": "..." },
    "2": { "label": "New Reader", "wordCount": 480, "text": "..." },
    "3": { "label": "On Your Own", "wordCount": 880, "text": "..." }
  }
}
```

### 3. Write three reading levels

Every book has three versions of the same story, written at different reading levels:

| Level | Label | Age | Length | Vocab | Pedagogy |
|-------|-------|-----|--------|-------|----------|
| 1 | Little Listener | 3–5 | 150–250 words | common words only | repetition, rhyme, one embedded lesson, sensory language |
| 2 | New Reader | 5–7 | 400–600 words | grade-appropriate, 1–2 new words defined in context | cause/effect, character growth, gentle moral |
| 3 | On Your Own | 7–10 | 800–1200 words | rich vocab, figurative language welcome | dialogue, multiple themes, end with an open question |

It's the **same story** at three levels — same characters, same arc — written with different vocabulary and depth.

### 4. Voice

- Warm, specific, never cute or saccharine
- Concrete sensory detail over abstract feeling
- Trust the reader — show, don't explain
- The lesson is tucked inside, never announced

### 5. Cover illustration

Inline SVG only (no external images). Keep it simple — a few shapes, the warm palette. Use the design tokens:
- Cream `#FBF6EE` / Cream-soft `#F5EFE3`
- Sage `#8FA68A` / Sage-deep `#5E7B5F`
- Amber `#D4925E` / Amber-deep `#B26F3D`
- Coral `#D67A6E` / Rust `#A8543F`
- Ink `#2A2118`

### 6. coverColor

Pick the background palette: `amber`, `sage`, `coral`, or `cream`.

### 7. Submit a PR

That's it. One folder, one file, one PR.

## Code contributions

Bug fixes, accessibility improvements, and small features are welcome. For anything larger, open an issue first to discuss.

```sh
npm install
npm run dev
```

Stick to:
- TypeScript strict mode
- The warm/cozy design palette (see `src/styles/global.css`)
- No new dependencies without discussion
- No tracking, no analytics, no third-party scripts that fingerprint users
