# CLAUDE.md — Fablewick

Project conventions for any Claude session working in this repo.

## What this is
Fablewick is an open-source AI storybook library for kids. Two modes: curated library + "Create your own" AI generation. Warm, cozy, ad-free, donation-supported (eventually).

## Voice for stories
- Warm, specific, never cute or saccharine
- Concrete sensory detail over abstract feeling
- Show, don't explain — trust the child reader
- The lesson is tucked inside, never announced
- End at the right moment — sometimes that's a small realization, sometimes an open question, never a moral

## Design system (see src/styles/global.css)
- Palette: cream `#FBF6EE`, ink `#2A2118`, sage `#8FA68A`, amber `#D4925E`, coral `#D67A6E`
- Display: Fraunces (serif, optical-sized)
- Body: Lora (serif)
- UI: Outfit (sans)
- Radii: 12px (soft) / 20px (warm) / 28px (cozy)

## Architecture
- Astro 6 (static-first, content collections, React islands)
- Tailwind 4 via @tailwindcss/vite (NOT classic Tailwind config)
- AI generation via Cloudflare Pages Functions in `functions/api/`
- Provider-agnostic AI layer in `src/lib/ai-provider.ts` (Gemini primary, Claude fallback)
- No database — books are JSON in `src/content/books/`
- No accounts, no tracking, COPPA-safe by design

## Adding a book
A new book = one folder under `src/content/books/<slug>/` with `meta.json`. See CONTRIBUTING.md.

## Don't do
- Don't add accounts, sign-ups, or user-tracking analytics
- Don't add tracking pixels, fingerprinting, or third-party scripts that profile users
- Don't add a paywall or premium tier
- Don't introduce a database without serious discussion
- Don't switch to Tailwind classic config — we're on Tailwind 4 with @theme directives
- Don't add commentary inside generated stories ("The End", framing notes, etc.) — story-only output

## Commands
```sh
npm install     # install deps
npm run dev     # local dev at :4321
npm run build   # production build to ./dist
npm run preview # preview the build
```
