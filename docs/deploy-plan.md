# Fablewick — Deploy Plan (GitHub → public URL)

*Drafted 2026-06-12 from a full repo recon. Status: PLAN — nothing pushed. Mann reviews, then "go".*

## 0. The one decision that shapes everything

Two things could go live; they are not the same:

| Option | What ships | Effort to public URL |
|---|---|---|
| **A. Library readers (static)** — `library/` | The 11 self-contained readers + landing, exactly what works locally today. No build step, no API. | **Near zero** — push + enable Pages |
| **B. Astro site** — `src/` + `functions/` | The "real" product: book pages w/ 3 levels, Create-your-own AI generation. **But:** Astro pages don't yet render the new page art (only SVG covers), and `/api/generate` needs Cloudflare + API keys. | Medium — needs an art-wiring pass + Cloudflare setup |

**Recommendation: ship A now** (it's finished and beautiful), keep B as phase 2 (wire art into Astro templates, then move to Cloudflare Pages with the same repo). The repo can hold both from day one.

## 1. What goes INTO the GitHub repo

```
fablewick/  (Mann's existing GitHub repo)
├── library/                  ← the live site (Pages serves this)
│   ├── index.html            ← RENAMED from fablewick-landing.html (required for Pages root)
│   ├── reader-*.html  ×11
│   └── reader-*.i18n.json ×11
├── src/                      ← Astro source incl. content/books/*/meta.json (canonical text)
│   └── assets/ — JPG art only (heroes/ + pages/*/page-0N.jpg + cover.jpg + logo)
├── public/  functions/  scripts/  translations/  docs/
├── astro.config.mjs  package.json  package-lock.json  tsconfig.json
├── README.md  LICENSE  CONTRIBUTING.md  CLAUDE.md  .gitignore
```

## 2. What does NOT go (and why)

| Excluded | Why | Action before push |
|---|---|---|
| `src/assets/mann-headshot-grey-2026.png` | **Personal photo — privacy.** Recon flagged it; I copied it in for the local landing only. | Delete from repo copy; local landing keeps it via `.gitignore` OR strip the About-photo block from the public `index.html` (default: strip — public ≠ private rule) |
| `src/assets/pages/**/*.png` (66 masters, ~630 MB) | Repo bloat; the readers use the JPGs. PNGs are the archive masters. | `.gitignore` `*.png` under pages/; masters stay local (or move to `3-Input/fablewick-masters/`) |
| `node_modules/`, `dist/`, `.astro/`, `.env*` | Standard | already in `.gitignore` |
| `.git-backup/` | Old local-only git history (2 commits, no remote) — superseded | delete or keep local; never push |
| `docs/genai-stack-comparison…`, `_mobile-preview.html`, `_rewrite/` | Internal research / build intermediates | `.gitignore` or local-only |
| `demo-reel.pdf`, `image-audit.html` | Internal review artifacts | local-only |
| `library/index.html` About section | Contains Mann's name/photo — Mann decides what bio goes public | review line-by-line pre-push |

## 3. Pre-push fixes (small, concrete)

1. Rename `fablewick-landing.html` → `index.html` inside `library/` (update nothing else — reader links are relative).
2. Strip/neutralize the About-me block (photo + personal lines) in the public copy — Mann's call on what bio text stays.
3. Add `site: 'https://<final-domain>'` to `astro.config.mjs` (needed for SEO/canonical when Astro phase ships).
4. Extend `.gitignore`: `src/assets/pages/**/*.png`, `src/assets/mann-headshot*`, `_rewrite/`, `_mobile-preview.html`, `.git-backup/`.
5. Verify no other personal strings: recon already swept (clean apart from headshot).

## 4. Hosting path (Option A)

- **GitHub Pages**, serve from `library/` (via Pages "deploy from branch" + root=/library, or a 5-line Action that publishes `library/` to `gh-pages`).
- URL: `https://<user>.github.io/<repo>/` immediately; custom domain later (CNAME).
- Total cost: $0. No keys, no functions, COPPA-safe static.
- Phase 2 (Astro + AI generation): move hosting to **Cloudflare Pages** on the same repo (build `npm run build`, output `dist/`, bind `GEMINI_API_KEY` + optional `ANTHROPIC_API_KEY` + KV for rate-limit). GitHub Pages keeps serving until cutover.

## 5. Push mechanics (when Mann says go)

```
# inside 1-Projects/fablewick — uses Mann's existing fablewick repo
git init (or git remote add origin <existing-repo-url>)
apply §3 fixes → commit "fablewick v1: library + site source" → push
enable Pages → verify public URL on phone
```
Workspace repo (claude-online) stays the private master; the fablewick repo is the public mirror. Same pattern as mann-landing: a `publish`-style path map can automate workspace→public sync later.

## 6. Open items for Mann

- [ ] Confirm Option A first (static library now, Astro later)
- [ ] Repo URL of the existing Fablewick GitHub
- [ ] About-section bio: what text/photo (if any) goes public
- [ ] Logo pick (2 contenders in `src/assets/logo-contenders/`) — ships in v1 if chosen
- [ ] Custom domain? (e.g. fablewick.org — ~$7.50/yr, the only cost)
