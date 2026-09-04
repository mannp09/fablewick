# Ramkabir Heritage Edition, adults Hindi + Gujarati, brought in line with the reduced English

Wave: text apply (adults translations), continuing `docs/text-reduction-applied-2026-09-04.md`,
which completed English (all levels) and Kids-level Hindi/Gujarati but left Adults and Seniors
Hindi/Gujarati untouched. This wave closes the Adults half for both languages, all 5 stories.
Seniors is out of scope here (owned by a parallel run on the same file).

## Method

Same method as the Kids-level pass, applied per page:

1. Compare the pre-reduction (old) English page to the current (old) Hindi/Gujarati page.
2. Mirror the exact kind of cut the English reduction made at the corresponding spot in the
   translation: drop the same repeated or intensifying word, merge the same two sentences,
   turn the same em dash into a comma, drop the same restated clause.
3. Where the English page was left completely unchanged by the reduction, the translation page
   was left unchanged too (never trimmed on its own initiative).
4. Where the translation had already reached the reduced-English shape on its own (rare, one
   page — see below), it was reverted to its original wording rather than force a cut that would
   have made it longer.
5. No em dashes, no middots, in any new text. Existing punctuation conventions preserved
   otherwise. Proper nouns kept their existing spellings. Page count per story/level is
   unchanged (arrays are edited in place by index, never resized).

Verified after every apply: no page's new character count exceeds its old character count, and
the Kids-level arrays for all 5 stories are byte-identical before and after (hash below) — this
run touched only `levels.adults.hi` and `levels.adults.gu`.

One correction made mid-wave: `my-ram-is-everywhere` Gujarati page 9 was first drafted with an
extra conjunction that made it 101 characters against an old count of 99 (a real violation of
the shrink rule, though under the apply script's 5% flag threshold, so it applied silently).
Caught on the post-write audit and reverted to its original wording — the source line already
used the adjectival, comma-joined form ("warm, easy") that mirrors what the English page cut
*to*, so no further safe trim existed without cutting content the English still carries.

## Patch files (scratchpad, not committed — one-shot inputs to `apply-translations.py`)

- `dry-banyan-twig.json` (reused from an earlier interrupted run — parsed clean, covered all
  12 pages for both languages, every page shorter; applied as-is)
- `the-foot-that-said-ram.json` (earlier partial file only covered 18/28 pages — redone from
  scratch, all 28 pages both languages)
- `my-ram-is-everywhere.json` (new, all 10 pages both languages; one page corrected post-hoc,
  see above)
- `flowers-under-the-cloth.json` (new, 18 of 19 pages touched; page 13 left unchanged)
- `jivanjis-green-field.json` (new, all 13 pages both languages)
- `fix-my-ram-p9.json` (one-page correction patch, Gujarati page 9 of `my-ram-is-everywhere`)

## Per story, per language

Page counts equal the English page counts in every case (12 / 28 / 10 / 19 / 13).

### The Dry Banyan Twig — 12 pages

| Page | HI old→new (chars) | GU old→new (chars) |
|---|---|---|
| 1 | 182→165 | 182→165 |
| 2 | 151→138 | 150→135 |
| 3 | 299→283 | 286→273 |
| 4 | 259→237 | 266→243 |
| 5 | 96→89 | 93→87 |
| 6 | 285→256 | 307→266 |
| 7 | 149→127 | 140→110 |
| 8 | 218→191 | 236→204 |
| 9 | 94→91 | 82→78 |
| 10 | 254→219 | 234→212 |
| 11 | 103→97 | 114→109 |
| 12 | 360→315 | 356→325 |

Totals: HI 2450→2208 chars (**9.9% cut**); GU 2446→2207 chars (**9.8% cut**).
English adults shrink for this story: **16.2% cut**. No pages left unchanged.

### The Foot That Said Ram — 28 pages

| Page | HI old→new (chars) | GU old→new (chars) |
|---|---|---|
| 1 | 393→356 | 382→345 |
| 2 | 61→61 (unchanged) | 62→62 (unchanged) |
| 3 | 317→300 | 336→322 |
| 4 | 142→122 | 152→136 |
| 5 | 64→64 (unchanged) | 52→52 (unchanged) |
| 6 | 103→92 | 97→83 |
| 7 | 140→120 | 129→109 |
| 8 | 100→75 | 105→82 |
| 9 | 223→191 | 225→190 |
| 10 | 140→125 | 135→122 |
| 11 | 145→139 | 143→133 |
| 12 | 357→295 | 365→319 |
| 13 | 169→155 | 181→168 |
| 14 | 189→167 | 182→162 |
| 15 | 11→11 (unchanged) | 11→11 (unchanged) |
| 16 | 209→197 | 198→186 |
| 17 | 58→58 (unchanged) | 51→51 (unchanged) |
| 18 | 104→98 | 98→92 |
| 19 | 11→11 (unchanged) | 11→11 (unchanged) |
| 20 | 46→46 (unchanged) | 49→49 (unchanged) |
| 21 | 66→66 (unchanged) | 62→62 (unchanged) |
| 22 | 219→193 | 209→180 |
| 23 | 215→181 | 192→166 |
| 24 | 391→353 | 395→368 |
| 25 | 206→192 | 209→191 |
| 26 | 53→53 (unchanged) | 47→47 (unchanged) |
| 27 | 74→74 (unchanged) | 77→77 (unchanged) |
| 28 | 114→112 | 122→118 |

Totals: HI 4320→3907 chars (**9.6% cut**); GU 4277→3894 chars (**9.0% cut**).
English adults shrink for this story: **15.4% cut**.
Pages left unchanged (9): 2, 5, 15, 17, 19, 20, 21, 26, 27 — the English reduction pass made no
edit at all to these pages (verbatim in the reduction doc), so the translation was left verbatim
too.

### My Ram Is Everywhere — 10 pages

| Page | HI old→new (chars) | GU old→new (chars) |
|---|---|---|
| 1 | 231→214 | 233→213 |
| 2 | 190→175 | 195→179 |
| 3 | 229→211 | 246→223 |
| 4 | 227→224 | 241→233 |
| 5 | 175→164 | 156→145 |
| 6 | 188→179 | 191→181 |
| 7 | 158→150 | 169→161 |
| 8 | 195→188 | 204→197 |
| 9 | 116→111 | 99→99 (unchanged, see method note) |
| 10 | 167→156 | 173→160 |

Totals: HI 1876→1772 chars (**5.5% cut**); GU 1907→1791 chars (**6.1% cut**).
English adults shrink for this story: **11.4% cut**.
Pages left unchanged (1, Gujarati only): page 9 — see the correction note above; the Gujarati
line already carried the adjectival, comma-joined form the English page reduced *to*, so nothing
further could be cut without touching content the English still keeps. Hindi page 9 did have a
clean equivalent cut available and was trimmed normally.

### The Flowers Under the Cloth — 19 pages

| Page | HI old→new (chars) | GU old→new (chars) |
|---|---|---|
| 1 | 409→393 | 390→369 |
| 2 | 297→284 | 283→266 |
| 3 | 220→210 | 215→209 |
| 4 | 229→226 | 217→213 |
| 5 | 368→332 | 360→328 |
| 6 | 157→154 | 143→138 |
| 7 | 78→71 | 83→72 |
| 8 | 174→170 | 162→160 |
| 9 | 194→178 | 186→172 |
| 10 | 359→301 | 358→307 |
| 11 | 238→217 | 253→230 |
| 12 | 294→272 | 305→283 |
| 13 | 35→35 (unchanged) | 33→33 (unchanged) |
| 14 | 397→363 | 425→379 |
| 15 | 169→143 | 184→151 |
| 16 | 207→177 | 190→157 |
| 17 | 304→295 | 320→299 |
| 18 | 251→198 | 277→220 |
| 19 | 80→79 | 77→76 |

Totals: HI 4460→4098 chars (**8.1% cut**); GU 4461→4062 chars (**8.9% cut**).
English adults shrink for this story: **13.8% cut**.
Pages left unchanged (1): page 13 — the English reduction pass made no edit to this page
("And there was no weaver beneath it at all." verbatim), so the translation was left verbatim.

### Jivanji's Green Field — 13 pages

| Page | HI old→new (chars) | GU old→new (chars) |
|---|---|---|
| 1 | 368→325 | 349→314 |
| 2 | 407→354 | 351→303 |
| 3 | 386→362 | 372→349 |
| 4 | 290→250 | 285→249 |
| 5 | 493→457 | 473→441 |
| 6 | 380→360 | 393→377 |
| 7 | 554→510 | 538→497 |
| 8 | 385→368 | 340→326 |
| 9 | 423→349 | 423→351 |
| 10 | 536→486 | 498→458 |
| 11 | 331→294 | 334→308 |
| 12 | 504→425 | 481→405 |
| 13 | 183→163 | 170→149 |

Totals: HI 5240→4703 chars (**10.2% cut**); GU 5007→4527 chars (**9.6% cut**).
English adults shrink for this story: **15.1% cut**.
No pages left unchanged. (Two pages — 3 and 8 — carried pre-existing content with no English
counterpart at all, e.g. an extra clause about wheat sprouting on page 3; that drift content was
trimmed rather than preserved, since it was not being "kept" against an English cut, and doing
so also shortened the page. This is the same pre-existing-drift situation the Kids-level wave
documented; it was not otherwise touched.)

## All 5 stories, adults level, totals

| Lang | Old chars | New chars | Shrink |
|---|---|---|---|
| hi | 18,346 | 16,688 | **9.0% cut** |
| gu | 18,098 | 16,481 | **8.9% cut** |

English adults shrink across all 5 stories (word-weighted): **14.6% cut** (3792→3238 words).
The translations shrank by a smaller percentage than the English — expected, since Hindi/Gujarati
prose absorbs comma-merges and dropped intensifiers with less character reduction per cut than
English word-drops give, and several pages already ran tighter than their English counterparts
before this pass.

## Kids-level integrity check

Hash of `levels.kids` (Hindi + Gujarati, all 5 stories), before and after this run:

```
before: 57d6a3a7bb0b08064e63b8d6a38ebf86924463d92cfc3c9ce370cf59e70bde65
after:  57d6a3a7bb0b08064e63b8d6a38ebf86924463d92cfc3c9ce370cf59e70bde65
match:  True
```

Identical — this run never touched `levels.kids`, consistent with every patch file only ever
naming `"adults"` as the level key. `levels.seniors` changed during this run (confirmed by a
separate hash check), which is expected: a parallel agent owns Seniors on the same file, and the
apply script re-reads `library/ramkabir-fablewick.html` from disk on every invocation, so this
run's writes were always layered on top of whatever Seniors state was current at that moment,
never on a stale copy.

## Verification run

```
python scripts/apply-translations.py --dry-run <each patch>.json   # 0 errors, 0 flags, every dry run
python scripts/apply-translations.py <each patch>.json             # applied in order, one story at a time
```

Post-write audit (this session, not part of the apply script): iterated every one of the 164
adults pages (82 pages × 2 languages) and asserted new character count ≤ old character count —
0 violations after the page-9 correction — and scanned every new page for em dashes (`—`) and
middots (`·`) — 0 found.
