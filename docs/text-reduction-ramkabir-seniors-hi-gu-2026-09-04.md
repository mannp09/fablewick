# Ramkabir Heritage Edition -- Seniors hi/gu reduction, 2026-09-04

## Method

Applied to the SENIORS level's Hindi and Gujarati pageTexts for all 5 Ramkabir Heritage
Edition stories, to match the English text reductions already applied at all three levels
(see `docs/text-reduction-ramkabir-2026-09-04.md`). Same method as the kids-level pass
(`docs/text-reduction-applied-2026-09-04.md`): for each page, the CURRENT (pre-reduction)
English was compared to the REDUCED English to identify exactly what was cut or merged;
the analogous cut was made in the existing Hindi/Gujarati translation, using only that
translation's own vocabulary -- never a fresh retranslation, never new content. A page whose
English change was a single function word with no clean analogue in the translation was left
unchanged. Applied via `python scripts/apply-translations.py <patch.json>`, dry-run first on
every patch, `pageTexts` per level per language inside the `BOOKS` literal in
`library/ramkabir-fablewick.html`.

## Per-story results

### The Dry Banyan Twig

English seniors shrink (from the approved draft): 13.0% cut

**hi** -- pages: 12 (unchanged) -- 2906 -> 2744 chars -- 5.6% cut (English: 13.0%)

| Page | Old chars | New chars | Delta | Changed |
|---|---|---|---|---|
| 1 | 329 | 313 | 16 | yes |
| 2 | 229 | 215 | 14 | yes |
| 3 | 233 | 224 | 9 | yes |
| 4 | 248 | 227 | 21 | yes |
| 5 | 167 | 167 | 0 | NO -- left as is |
| 6 | 307 | 289 | 18 | yes |
| 7 | 153 | 139 | 14 | yes |
| 8 | 148 | 134 | 14 | yes |
| 9 | 112 | 109 | 3 | yes |
| 10 | 366 | 343 | 23 | yes |
| 11 | 142 | 142 | 0 | NO -- left as is |
| 12 | 472 | 442 | 30 | yes |

**gu** -- pages: 12 (unchanged) -- 2799 -> 2639 chars -- 5.7% cut (English: 13.0%)

| Page | Old chars | New chars | Delta | Changed |
|---|---|---|---|---|
| 1 | 320 | 306 | 14 | yes |
| 2 | 216 | 203 | 13 | yes |
| 3 | 229 | 222 | 7 | yes |
| 4 | 249 | 226 | 23 | yes |
| 5 | 161 | 161 | 0 | NO -- left as is |
| 6 | 298 | 282 | 16 | yes |
| 7 | 135 | 123 | 12 | yes |
| 8 | 154 | 140 | 14 | yes |
| 9 | 104 | 100 | 4 | yes |
| 10 | 321 | 297 | 24 | yes |
| 11 | 150 | 150 | 0 | NO -- left as is |
| 12 | 462 | 429 | 33 | yes |

### The Foot That Said Ram

English seniors shrink (from the approved draft): 9.2% cut

**hi** -- pages: 14 (unchanged) -- 3235 -> 3103 chars -- 4.1% cut (English: 9.2%)

| Page | Old chars | New chars | Delta | Changed |
|---|---|---|---|---|
| 1 | 214 | 211 | 3 | yes |
| 2 | 275 | 267 | 8 | yes |
| 3 | 154 | 138 | 16 | yes |
| 4 | 284 | 265 | 19 | yes |
| 5 | 231 | 227 | 4 | yes |
| 6 | 328 | 310 | 18 | yes |
| 7 | 120 | 117 | 3 | yes |
| 8 | 11 | 11 | 0 | NO -- left as is |
| 9 | 273 | 255 | 18 | yes |
| 10 | 159 | 149 | 10 | yes |
| 11 | 227 | 214 | 13 | yes |
| 12 | 522 | 515 | 7 | yes |
| 13 | 303 | 290 | 13 | yes |
| 14 | 134 | 134 | 0 | NO -- left as is |

**gu** -- pages: 14 (unchanged) -- 3184 -> 3049 chars -- 4.2% cut (English: 9.2%)

| Page | Old chars | New chars | Delta | Changed |
|---|---|---|---|---|
| 1 | 201 | 198 | 3 | yes |
| 2 | 280 | 273 | 7 | yes |
| 3 | 149 | 133 | 16 | yes |
| 4 | 277 | 255 | 22 | yes |
| 5 | 233 | 229 | 4 | yes |
| 6 | 341 | 322 | 19 | yes |
| 7 | 114 | 110 | 4 | yes |
| 8 | 11 | 11 | 0 | NO -- left as is |
| 9 | 252 | 234 | 18 | yes |
| 10 | 166 | 159 | 7 | yes |
| 11 | 208 | 197 | 11 | yes |
| 12 | 525 | 512 | 13 | yes |
| 13 | 294 | 283 | 11 | yes |
| 14 | 133 | 133 | 0 | NO -- left as is |

### My Ram Is Everywhere

English seniors shrink (from the approved draft): 11.7% cut

**hi** -- pages: 9 (unchanged) -- 3252 -> 3122 chars -- 4.0% cut (English: 11.7%)

| Page | Old chars | New chars | Delta | Changed |
|---|---|---|---|---|
| 1 | 351 | 335 | 16 | yes |
| 2 | 264 | 251 | 13 | yes |
| 3 | 340 | 333 | 7 | yes |
| 4 | 336 | 317 | 19 | yes |
| 5 | 350 | 336 | 14 | yes |
| 6 | 325 | 316 | 9 | yes |
| 7 | 477 | 466 | 11 | yes |
| 8 | 413 | 386 | 27 | yes |
| 9 | 396 | 382 | 14 | yes |

**gu** -- pages: 9 (unchanged) -- 3150 -> 3027 chars -- 3.9% cut (English: 11.7%)

| Page | Old chars | New chars | Delta | Changed |
|---|---|---|---|---|
| 1 | 350 | 332 | 18 | yes |
| 2 | 246 | 234 | 12 | yes |
| 3 | 322 | 314 | 8 | yes |
| 4 | 342 | 325 | 17 | yes |
| 5 | 294 | 282 | 12 | yes |
| 6 | 318 | 309 | 9 | yes |
| 7 | 470 | 458 | 12 | yes |
| 8 | 416 | 397 | 19 | yes |
| 9 | 392 | 376 | 16 | yes |

### The Flowers Under the Cloth

English seniors shrink (from the approved draft): 11.1% cut

**hi** -- pages: 14 (unchanged) -- 3575 -> 3396 chars -- 5.0% cut (English: 11.1%)

| Page | Old chars | New chars | Delta | Changed |
|---|---|---|---|---|
| 1 | 333 | 303 | 30 | yes |
| 2 | 394 | 376 | 18 | yes |
| 3 | 166 | 163 | 3 | yes |
| 4 | 336 | 319 | 17 | yes |
| 5 | 120 | 115 | 5 | yes |
| 6 | 479 | 473 | 6 | yes |
| 7 | 187 | 176 | 11 | yes |
| 8 | 264 | 249 | 15 | yes |
| 9 | 35 | 35 | 0 | NO -- left as is |
| 10 | 367 | 341 | 26 | yes |
| 11 | 302 | 284 | 18 | yes |
| 12 | 287 | 279 | 8 | yes |
| 13 | 225 | 204 | 21 | yes |
| 14 | 80 | 79 | 1 | yes |

**gu** -- pages: 14 (unchanged) -- 3472 -> 3301 chars -- 4.9% cut (English: 11.1%)

| Page | Old chars | New chars | Delta | Changed |
|---|---|---|---|---|
| 1 | 297 | 271 | 26 | yes |
| 2 | 384 | 364 | 20 | yes |
| 3 | 159 | 154 | 5 | yes |
| 4 | 312 | 296 | 16 | yes |
| 5 | 117 | 117 | 0 | NO -- left as is |
| 6 | 459 | 454 | 5 | yes |
| 7 | 188 | 177 | 11 | yes |
| 8 | 257 | 244 | 13 | yes |
| 9 | 33 | 33 | 0 | NO -- left as is |
| 10 | 387 | 356 | 31 | yes |
| 11 | 283 | 268 | 15 | yes |
| 12 | 280 | 272 | 8 | yes |
| 13 | 239 | 219 | 20 | yes |
| 14 | 77 | 76 | 1 | yes |

### Jivanji's Green Field

English seniors shrink (from the approved draft): 13.6% cut

**hi** -- pages: 8 (unchanged) -- 3464 -> 3276 chars -- 5.4% cut (English: 13.6%)

| Page | Old chars | New chars | Delta | Changed |
|---|---|---|---|---|
| 1 | 383 | 376 | 7 | yes |
| 2 | 377 | 336 | 41 | yes |
| 3 | 327 | 305 | 22 | yes |
| 4 | 563 | 552 | 11 | yes |
| 5 | 527 | 509 | 18 | yes |
| 6 | 458 | 427 | 31 | yes |
| 7 | 475 | 446 | 29 | yes |
| 8 | 354 | 325 | 29 | yes |

**gu** -- pages: 8 (unchanged) -- 3283 -> 3099 chars -- 5.6% cut (English: 13.6%)

| Page | Old chars | New chars | Delta | Changed |
|---|---|---|---|---|
| 1 | 325 | 318 | 7 | yes |
| 2 | 372 | 333 | 39 | yes |
| 3 | 304 | 280 | 24 | yes |
| 4 | 541 | 532 | 9 | yes |
| 5 | 515 | 494 | 21 | yes |
| 6 | 414 | 380 | 34 | yes |
| 7 | 474 | 450 | 24 | yes |
| 8 | 338 | 312 | 26 | yes |

## Pages left unchanged, and why

Every page below had an English change limited to a single function word or particle with
no clean analogue in the existing Hindi/Gujarati translation (or the translation was already
at floor length for its content), so it was left byte-identical rather than force a cut:

- The Dry Banyan Twig -- hi page 5
- The Dry Banyan Twig -- hi page 11
- The Dry Banyan Twig -- gu page 5
- The Dry Banyan Twig -- gu page 11
- The Foot That Said Ram -- hi page 8
- The Foot That Said Ram -- hi page 14
- The Foot That Said Ram -- gu page 8
- The Foot That Said Ram -- gu page 14
- The Flowers Under the Cloth -- hi page 9
- The Flowers Under the Cloth -- gu page 5
- The Flowers Under the Cloth -- gu page 9

## Kids level integrity check

The kids level was not touched this run (owned by a separate concurrent agent's story-editing
pass only at the seniors level for this task -- kids had already been finished in an earlier
wave). Hash is SHA-256 of the kids-level JSON (`hi`+`gu`+`en` pageTexts/covers/ends) per story,
compared between the session-start HEAD commit and the current working file:

| Story | Kids hash before | Kids hash after | Match |
|---|---|---|---|
| The Dry Banyan Twig | `83487c77f7bd0f48` | `83487c77f7bd0f48` | yes |
| The Foot That Said Ram | `b780a4ed11ac0775` | `b780a4ed11ac0775` | yes |
| My Ram Is Everywhere | `14c124bdaf73d9b9` | `14c124bdaf73d9b9` | yes |
| The Flowers Under the Cloth | `21b588ff12436908` | `21b588ff12436908` | yes |
| Jivanji's Green Field | `98d5269c0b2d947d` | `98d5269c0b2d947d` | yes |

Adults level was not asserted on -- it is being edited in parallel by another agent.
