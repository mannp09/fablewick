# Fablewick

> A quiet, open-source library of stories for kids. Free, ad-free, hand-curated.

Fablewick is two things in one place:

1. **A library** — hand-written stories for ages 3–10, each with three reading levels (Little Listener, New Reader, On Your Own) and a small lesson tucked inside.
2. **A story workshop** — describe a story you want, pick your reader's level, and a fresh one is written for you in about 20 seconds.

Free. No ads. No accounts. No tracking. No paywall. Ever.

## Why

The personalized children's book space is dominated by paid apps and AI-generation-as-a-product. Fablewick is the opposite: a curated library first, with AI generation as a quiet feature. Stories are warm, specific, and never preachy. Lessons are embedded, not announced.

It exists because storytelling is one of the oldest ways humans have taught each other to be kind, brave, patient, and curious.

## Stack

- **Astro 6** — static-first, content collections for books, React islands for interactivity
- **Tailwind CSS 4** — warm, cozy palette (cream, sage, amber, coral)
- **Cloudflare Pages + Pages Functions** — free-tier hosting, edge-rate-limited AI endpoint
- **AI generation** — Google Gemini 2.5 Flash (free tier, 1,500 req/day) → Claude Haiku fallback
- **No database** — books are JSON files in this repo. localStorage for per-reader preferences.

Total infrastructure cost: ~$7.50/year (domain only).

## Local development

Requires Node.js 22.12+.

```sh
npm install
npm run dev      # http://localhost:4321
npm run build    # production build to ./dist/
npm run preview  # preview the built site
```

### Environment variables

Create a `.env` file at the project root (see `.env.example`):

```
GEMINI_API_KEY=...      # primary: get free key at https://aistudio.google.com/app/apikey
ANTHROPIC_API_KEY=...   # fallback (optional)
```

For local development, AI generation works if either key is set.

## Project structure

```
fablewick/
├── README.md            you are here
├── CONTRIBUTING.md      how to add a book
├── CLAUDE.md            project conventions for Claude sessions
├── LICENSE              MIT
├── .env.example         copy to .env and fill in API keys
│
├── src/
│   ├── pages/           routes: /, /create, /book/[slug], /about
│   ├── components/      BookCard, StoryGenerator (React), Header, Footer
│   ├── layouts/         BaseLayout
│   ├── content/
│   │   └── books/       one folder per book, each with meta.json
│   ├── content.config.ts  schema for the books collection
│   ├── lib/
│   │   ├── reading-levels.ts  Pre-K / Early Reader / Independent definitions
│   │   ├── prompts.ts         AI system prompts per level
│   │   └── ai-provider.ts     Gemini → Claude fallback layer
│   └── styles/global.css      design tokens, palette, typography
│
├── functions/api/
│   └── generate.ts      Cloudflare Pages Function — rate-limited AI endpoint
│
├── scripts/
│   └── validate-books.py  checks every book before commit
│
└── public/              static assets (favicon)
```

## Commands

| Command | What it does |
|---------|-------------|
| `npm run dev` | local dev server at http://localhost:4321 |
| `npm run build` | production build → `./dist/` |
| `npm run preview` | preview the built site |
| `npm run check-books` | validate every book's structure and word counts |

## Project layout

| Folder | What lives there |
|---|---|
| `library/` | **Open these** — `fablewick-landing.html` + 11 `reader-*.html` (self-contained readers with art + translations), `demo-reel.pdf`, `image-audit.html` |
| `src/` | Astro site source — `src/content/books/<slug>/meta.json` is each book's canonical text (3 levels); `src/assets/pages/<slug>/` is its art (cover + 5 pages); `src/assets/logo-contenders/` |
| `docs/` | Character canon (`character-reference.md`), continuity rules (`continuity-protocol.md`), all image prompts (`gemini-prompts/`, `page-prompts/`, `hero-prompts.md`), stack research, old mockup |
| `translations/` | i18n source JSONs + `build_translations.py` |
| `scripts/` | `validate-books.py`, `inject_reader_text.py` (pushes meta.json rewrites into readers), `apply_continuity.py` |
| `public/`, `functions/` | Astro static assets + Cloudflare Pages Functions (AI generation endpoint) |

## Adding a book

Books are folders inside `src/content/books/`. To add one:

1. Create `src/content/books/your-book-slug/meta.json`
2. Fill in title, ageRange, themes, lesson, summary, coverColor, coverIllustration (inline SVG), and `levels` (1, 2, 3 with text)
3. Open a pull request

See `CONTRIBUTING.md` for the full guide and any existing book as a template.

## License

MIT. The stories in this repo are also released under MIT — use them freely, including for translation, adaptation, or commercial use.
