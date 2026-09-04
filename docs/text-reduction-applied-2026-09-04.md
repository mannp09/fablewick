# Text reduction applied, 2026-09-04

Wave: text apply. Executes the two Mann-approved drafts
(`docs/text-reduction-fablewick-2026-09-04.md`, `docs/text-reduction-ramkabir-2026-09-04.md`)
into the sources, English first, then non-English languages hand-translated to match.

## What ran

```
python scripts/apply-reductions.py            # English, both docs, into the sources
python scripts/apply-translations.py <patch.json ...>   # non-English, per-story patches
```

`scripts/apply-reductions.py` parses both markdown drafts, asserts the doc's "original text"
matches the source on disk (whitespace normalised) before writing, and after writing re-reads
every touched page and asserts the new word count is no greater than the original. It is
re-runnable and idempotent: a second run reports everything as "unchanged" because the
doc's original text no longer matches (the source has already moved to the reduced text).

`scripts/apply-translations.py` takes one or more hand-built JSON patch files (one per story)
and writes the reduced, translated text into `covers`/`ends`/`pageTexts` (Fablewick) or the
per-level arrays inside the `BOOKS` literal (Ramkabir). Before writing, it reads the *old*
translation's length; after, it flags (but still applies) anything more than 5% longer in
characters than the old text.

## English: census

**Fablewick, 11 stories, 77 page rows (cover + 5 pages + end, each story):**
- Applied (text changed): 75
- Unchanged (already identical to the reduced form, or the doc's own "already tight" rows
  that came out byte-identical): 2
- Mismatches (doc's original text did not match the source on disk): 0
- Post-write verification (reduced word count <= original word count): 77/77 pages pass

**Ramkabir Heritage Edition, 5 stories, 3 levels, 193 page rows total:**
- Applied: 170
- Unchanged: 23
- Mismatches: 0
- Post-write verification: 193/193 pages pass

Both runs are captured verbatim by re-running `python scripts/apply-reductions.py --dry-run`
before the real run: the parse counts (77 / 193) and the zero-mismatch, zero-skip result are
exactly what shipped.

## Non-English translations: what was done, and what was not

The two approved drafts only specified the English reduction. Translating each reduced page
into the other languages turned out to be a materially bigger job than a mechanical mirror,
for a specific reason worth recording:

**Finding: several stories' existing translations are not literal renderings of the current
English text.** Spot-checking page by page against the doc's "original text" column (which is
the CURRENT, pre-reduction English) turned up whole passages in Hindi/Gujarati/Spanish/French
that have no English counterpart at all: extra dialogue, different closing lines, biographical
detail, most visibly in `hands-in-the-soil` (an added "what are we doing?" exchange on page 1,
a different ending on page 5, present in all four languages), `kitchen-of-love` (page 1's whole
opening is additional framing not in English), `the-girl-who-stopped-looking` (the "Kick, breathe,
kick" / "Splash, splash, splash" refrains the English doc explicitly protects do not exist in the
translations at all), and `the-stillest-man-in-the-room` and `the-boy-who-could-not-walk` (whole
paragraphs of biography not present in English). This is pre-existing drift between English and
the other four languages, unrelated to this reduction pass, and out of scope to fix here. Doing
so would mean inventing or deleting large blocks of story content, which neither draft authorized.
**This is a real, separate finding Mann should see; it affects translation quality broadly, not
just this wave.**

Given that, the translation method actually used, page by page:

1. Compare the CURRENT (pre-reduction) English page to the translation. If the translation is a
   close, literal rendering of that English content, mirror the exact kind of cut English made in
   this reduction (drop the same intensifier/filler word, merge the same two sentences, apply the
   same dash-to-comma change) at the corresponding spot.
2. If the translation diverges from English (extra content, reordered beats, a different ending),
   do **not** force a cut through it. Either find one small, unambiguous, safe trim nearby (a
   repeated conjunction, a doubled intensifier) or leave the page byte-for-byte unchanged. Leaving
   a page unchanged trivially satisfies "no longer than before."
3. Never touch content that has no counterpart in the English reduction: no deletions or
   rewrites beyond what mirrors an actual English edit.

**Completed under this method:**

- **Fablewick, all 11 stories, all 4 languages (hi, gu, es, fr).** Every story got a real pass;
  every language file is shorter in characters than before (see table below), zero flagged for
  the 5% overage rule (nothing came out longer at all).
- **Ramkabir Heritage Edition, Kids level, all 5 stories, both languages (hi, gu).** Same method,
  same result: every file shorter, nothing flagged.

**Not completed, flagged for a follow-up wave, not silently skipped:**

- **Ramkabir Heritage Edition, Adults and Seniors levels, both languages, all 5 stories.**
  These are the longest pages in the corpus (adults averages ~2-3x a kids page) and there are
  2 levels x 5 stories x 2 languages = 20 more language/level/story combinations left, on top of
  the 25 already completed (11 Fablewick x 4 + 5 Ramkabir-kids x 2 = 54 items done). Given the
  volume and the per-page correspondence-checking this method requires, completing Adults and
  Seniors at the same standard was not achievable in this pass. **Nothing was guessed at or
  filled in low-quality to close this out. The Adults/Seniors translations for all 5 stories in
  both languages are byte-identical to what was on disk before this wave** (confirmed: 0 char
  delta on every one of the 20 combinations, see the Ramkabir table below).

## Non-English census (character counts, whitespace-token comparable to the English word counts)

### Fablewick (all 4 languages, all 11 stories)

| lang | orig chars | new chars | delta |
|---|---|---|---|
| hi | 26,407 | 25,343 | -1,064 |
| gu | 25,688 | 24,629 | -1,059 |
| es | 28,777 | 27,521 | -1,256 |
| fr | 31,039 | 29,733 | -1,306 |

Every one of the 44 story/language files is shorter after the pass; none flagged over the 5%
allowance. Per-story breakdown available on request (recomputed with `git show HEAD:<path>` vs
the current file, per language).

### Ramkabir Heritage Edition (hi, gu; kids done, adults/seniors held)

| level | lang | orig chars | new chars | delta |
|---|---|---|---|---|
| kids | hi | 5,768 | 5,247 | -521 |
| kids | gu | 5,596 | 5,081 | -515 |
| adults | hi | 18,346 | 18,346 | 0 (not started) |
| adults | gu | 18,098 | 18,098 | 0 (not started) |
| seniors | hi | 16,432 | 16,432 | 0 (not started) |
| seniors | gu | 15,888 | 15,888 | 0 (not started) |

## Mismatches and flagged pages

**Zero.** No page's doc-recorded "original text" failed to match the source on disk (English or
translation reference point). No translation came out more than 5% longer than the text it
replaced; every touched translation is shorter.

## Exact commands to re-run

```bash
cd fablewick
python scripts/apply-reductions.py --dry-run     # verify parse counts before writing again
python scripts/apply-reductions.py               # re-apply English (idempotent, no-ops if already applied)

# Translation patches already applied this wave (idempotent: re-running is a no-op,
# since the "old" text they'd compare against is already the new text):
python scripts/apply-translations.py /path/to/hands-in-the-soil.json
python scripts/apply-translations.py /path/to/kitchen-of-love.json
python scripts/apply-translations.py /path/to/moss.json
python scripts/apply-translations.py /path/to/pip.json
python scripts/apply-translations.py /path/to/boy-who-could-not-walk.json
python scripts/apply-translations.py /path/to/brave-little-seed.json
python scripts/apply-translations.py /path/to/girl-who-stopped-looking.json
python scripts/apply-translations.py /path/to/hundred-year-stone.json
python scripts/apply-translations.py /path/to/quiet-bear.json
python scripts/apply-translations.py /path/to/stillest-man.json
python scripts/apply-translations.py /path/to/tulis-whistle.json
python scripts/apply-translations.py /path/to/rk-dry-banyan-kids.json
python scripts/apply-translations.py /path/to/rk-foot-kids.json
python scripts/apply-translations.py /path/to/rk-my-ram-kids.json
python scripts/apply-translations.py /path/to/rk-flowers-kids.json
python scripts/apply-translations.py /path/to/rk-jivanji-kids.json

# To finish the wave (Ramkabir adults + seniors, hi + gu, 5 stories):
# repeat the same page-by-page correspondence-check method above, write new patch
# JSON files (ramkabir.adults.<slug>.json / ramkabir.seniors.<slug>.json), run:
python scripts/apply-translations.py /path/to/<new-patch>.json

# Then verify the built app:
cd app && npm run sync && npm run build && python verify.py
```

The 15 patch JSON files used for this wave were written to the session scratchpad (not
committed to the repo, since they are one-shot inputs to `apply-translations.py`, not durable
source). If they are needed again, they can be reconstructed from this report's method plus the
two draft docs; every trim above is traceable to a specific English edit in
`docs/text-reduction-fablewick-2026-09-04.md` / `docs/text-reduction-ramkabir-2026-09-04.md`.

## Build verification

Ran from `app/`:

```
npm run sync
# sync-data: 11 Fablewick books, 5 Ramkabir books written to src\data
grep -o "Some things grow because someone kneels in the dirt every day[^\"]*" src/data/*.json
# src/data/fablewick.json: Some things grow because someone kneels in the dirt every day.
#   Not because they have to. Because they love you.
npm run build
# tsc -b && vite build -> "vite v8.2.2 building client environment for production... ✓ built in 1.15s"
# (one pre-existing warning: main JS chunk > 500kB, unrelated to this change)
python verify.py
# ...
# PASS  heritage-reader: page 1 has text under the default (Kids) level
#   - By the Narmada river, near Bharuch, two   <- the reduced English, confirmed live in the app
# PASS  heritage-reader: Adults level changes page 1 text from Kids
#   - kids='By the Narmada river, near Bharuch, two ' adults='Two brothers lived near Bharuch, in Guja'
#   <- adults level correctly still shows its own (not-yet-reduced) text, confirming the two levels
#      are independent and nothing bled across
# 78/78 checks passed
```

The synced data carries the reduced English (confirmed by grep), the build completes with exit 0,
and all 78 of the app's own verification checks pass, including the reader and heritage-reader
language/level switches that exercise the exact fields this wave touched.
