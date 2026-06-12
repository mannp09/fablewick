# Fablewick — Gemini generation run log (2026-06-11)

Autonomous run: all-new covers + 5 interior pages per book, generated on **Gemini web (Pro / Nano Banana)** via browser harness. Mann's go: "finish fablewick... utilize gemini for pictures - and continuity... no intervention."

## Method (what actually worked)
- One Gemini **chat per book** — in-session memory holds the characters; first message carries STYLE ANCHOR + verbatim character block + cover scene; pages sent as "Approved. Create an image - PAGE N: <scene>... Same characters, same style."
- **Start every prompt with "Create an image:"** — without it Pro sometimes answers in text and *hallucinates that it rendered* (happened twice in one chat; abandoned that chat).
- Send via **DOM injection** into the Quill composer + click Send button (keyboard typing raced the page hydration twice and sent blank/dash messages; Return-to-send is unreliable).
- Download each accepted render via the image card's "Download full size" → lands in `Downloads/Gemini_Generated_Image_*.png` → moved immediately to `src/assets/pages/<book>/`.
- Audit each render on screen (zoom when in doubt) against continuity-protocol reject criteria before "Approved."
- Renders are **2752×1536 PNG (RGBA)**, no visible watermark.

## Known issues / gotchas hit
- Gemini streams sometimes wedge ("Stop response" forever) → reload the conversation URL frees it; composer content is lost, re-inject.
- Reloading /app/<id> can silently start a NEW conversation on next send — character memory is gone, but a compact character recap in the prompt held continuity fine in practice.
- Navigating away <5s after clicking download can cancel it (pip page-05 lost this way — recover from its chat).
- Text-only hallucination chats: abandon and restart in a fresh chat with "Create an image:" lead.

## Status per book (chat URL · files)
| Book | Chat | Files filed |
|---|---|---|
| kitchen-of-love | /app/95cee5012ea2f904 (cover, via reload→ /app/ec54c39410e4499e for pages) | cover + page-01..05 + page-eating-candidate ✓ |
| the-quiet-bear | /app/aa250160e2ec4a5b | cover + page-01..05 ✓ |
| the-brave-little-seed | /app/0d25bd0953d67c1b (junk text-only: /app/ab134be973255764, abandoned) | cover + page-01..05 ✓ |
| pip-and-the-lost-cloud | /app/9fa726719cd84214 | cover + page-01..04 ✓ + page-05 ✓ (regenerated fresh after history loss) |
| moss-and-the-starry-night-sky | /app/427c3ce6d5f22871 | cover + page-01..04 ✓ + page-05 ✓ (regenerated fresh after history loss) |
| tulis-whistle | /app/d4fac27fdf8e5c7e | cover + page-01..05 ✓ |
| the-hundred-year-stone | /app/f08aad30fb8f5674 | cover + page-01..05 ✓ |
| the-boy-who-could-not-walk | /app/97421b7b180750ea | cover + page-01..05 ✓ |
| the-stillest-man-in-the-room | /app/871ae16859aa31ae | cover + page-01..04 ✓ + page-05 ✓ (regenerated fresh after history loss) |
| the-girl-who-stopped-looking | /app/aafa5fe1803a06a9 | cover + page-01..04 ✓ + page-05 ✓ (regenerated fresh after history loss) |
| hands-in-the-soil | — | pending (fresh Dada+child canon — same) |

Exact prompts per book: `<book>.md` in this folder.
