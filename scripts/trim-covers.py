#!/usr/bin/env python3
"""
Wave 1b - Covers ruling: trim the painted cream margin from every cover,
then one uniform 16:9 bleed crop, same recipe for every card.

Owns ONLY this script, library/assets/covers-trimmed/, and docs/covers-trim-sheet.png.
No image generation. Reads source covers only, never writes to them.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "library", "assets", "covers-trimmed")
SHEET_PATH = os.path.join(REPO, "docs", "covers-trim-sheet.png")

FABLEWICK_SLUGS = [
    "hands-in-the-soil",
    "kitchen-of-love",
    "moss-and-the-starry-night-sky",
    "pip-and-the-lost-cloud",
    "the-boy-who-could-not-walk",
    "the-brave-little-seed",
    "the-girl-who-stopped-looking",
    "the-hundred-year-stone",
    "the-quiet-bear",
    "the-stillest-man-in-the-room",
    "tulis-whistle",
]

RAMKABIR_SLUGS = [
    "dry-banyan-twig",
    "flowers-under-the-cloth",
    "jivanjis-green-field",
    "my-ram-is-everywhere",
    "the-foot-that-said-ram",
]

RING_PX = 6
TOL = 12  # Fable: tighter, the deckle is semi-cream
ROW_COL_CONTENT_FRAC = 0.08  # Fable: a row is content only when 8 percent of it is paint
EXPAND_FRAC = -0.04  # Fable: INSET 4 percent per side so the crop sits inside the torn watercolour edge
TARGET_RATIO = 16.0 / 9.0
VERTICAL_BIAS_ABOVE = 0.40
MIN_KEPT_FRAC = 0.70
MIN_EDGE_STD = 14.0


def source_path(slug, is_ramkabir):
    if is_ramkabir:
        return os.path.join(REPO, "library", "assets", "ramkabir", slug, "cover.jpg")
    return os.path.join(REPO, "src", "assets", "pages", slug, "cover.jpg")


def output_stub(slug, is_ramkabir):
    return f"heritage-{slug}" if is_ramkabir else slug


def estimate_margin_color(arr):
    h, w = arr.shape[0], arr.shape[1]
    ring = np.concatenate([
        arr[:RING_PX, :, :].reshape(-1, 3),
        arr[-RING_PX:, :, :].reshape(-1, 3),
        arr[:, :RING_PX, :].reshape(-1, 3),
        arr[:, -RING_PX:, :].reshape(-1, 3),
    ])
    return np.median(ring, axis=0)


def content_box(arr, margin_color):
    h, w = arr.shape[0], arr.shape[1]
    diff = np.abs(arr.astype(int) - margin_color.astype(int))
    bg_mask = np.all(diff <= TOL, axis=2)
    content_mask = ~bg_mask

    row_frac = content_mask.mean(axis=1)
    col_frac = content_mask.mean(axis=0)

    top = 0
    for r in range(h):
        if row_frac[r] > ROW_COL_CONTENT_FRAC:
            top = r
            break
    bottom = h - 1
    for r in range(h - 1, -1, -1):
        if row_frac[r] > ROW_COL_CONTENT_FRAC:
            bottom = r
            break
    left = 0
    for c in range(w):
        if col_frac[c] > ROW_COL_CONTENT_FRAC:
            left = c
            break
    right = w - 1
    for c in range(w - 1, -1, -1):
        if col_frac[c] > ROW_COL_CONTENT_FRAC:
            right = c
            break

    return left, top, right, bottom


def expand_box(box, w, h):
    left, top, right, bottom = box
    cw = right - left + 1
    ch = bottom - top + 1
    ex = round(EXPAND_FRAC * cw)
    ey = round(EXPAND_FRAC * ch)
    new_left = max(0, left - ex)
    new_right = min(w - 1, right + ex)
    new_top = max(0, top - ey)
    new_bottom = min(h - 1, bottom + ey)
    return new_left, new_top, new_right, new_bottom


def fit_16x9(box):
    left, top, right, bottom = box
    box_w = right - left + 1
    box_h = bottom - top + 1

    if box_w / box_h > TARGET_RATIO:
        crop_h = box_h
        crop_w = crop_h * TARGET_RATIO
    else:
        crop_w = box_w
        crop_h = crop_w / TARGET_RATIO

    free_w = box_w - crop_w
    free_h = box_h - crop_h

    crop_left = left + free_w / 2.0
    crop_top = top + VERTICAL_BIAS_ABOVE * free_h
    crop_right = crop_left + crop_w
    crop_bottom = crop_top + crop_h

    kept_frac = (crop_w * crop_h) / (box_w * box_h)

    return (
        (int(round(crop_left)), int(round(crop_top)), int(round(crop_right)), int(round(crop_bottom))),
        kept_frac,
    )


def edge_std(arr):
    h, w = arr.shape[0], arr.shape[1]
    ring = np.concatenate([
        arr[:RING_PX, :, :].reshape(-1, 3),
        arr[-RING_PX:, :, :].reshape(-1, 3),
        arr[:, :RING_PX, :].reshape(-1, 3),
        arr[:, -RING_PX:, :].reshape(-1, 3),
    ])
    return float(np.std(ring))


def process_one(slug, is_ramkabir):
    src = source_path(slug, is_ramkabir)
    im = Image.open(src).convert("RGB")
    arr = np.array(im)
    h, w = arr.shape[0], arr.shape[1]

    margin_color = estimate_margin_color(arr)
    raw_box = content_box(arr, margin_color)
    exp_box = expand_box(raw_box, w, h)
    crop_box, kept_frac = fit_16x9(exp_box)

    # clamp crop box to image bounds (paranoia; expand + fit should already keep in range)
    cl, ct, cr, cb = crop_box
    cl = max(0, cl)
    ct = max(0, ct)
    cr = min(w, cr)
    cb = min(h, cb)
    crop_box = (cl, ct, cr, cb)

    cropped = im.crop(crop_box)
    out_1600 = cropped.resize((1600, 900), Image.LANCZOS)
    out_800 = cropped.resize((800, 450), Image.LANCZOS)

    stub = output_stub(slug, is_ramkabir)
    os.makedirs(OUT_DIR, exist_ok=True)
    path_1600 = os.path.join(OUT_DIR, f"{stub}.jpg")
    path_800 = os.path.join(OUT_DIR, f"{stub}-800.jpg")
    out_1600.save(path_1600, "JPEG", quality=88)
    out_800.save(path_800, "JPEG", quality=88)

    out_arr = np.array(out_1600)
    std = edge_std(out_arr)

    kept_ok = kept_frac >= MIN_KEPT_FRAC
    std_ok = std >= MIN_EDGE_STD

    result = {
        "slug": stub,
        "src": src,
        "src_size": (w, h),
        "raw_box": raw_box,
        "trims": {
            "left": raw_box[0],
            "top": raw_box[1],
            "right": w - 1 - raw_box[2],
            "bottom": h - 1 - raw_box[3],
        },
        "exp_box": exp_box,
        "crop_box": crop_box,
        "kept_frac": kept_frac,
        "kept_ok": kept_ok,
        "edge_std": std,
        "std_ok": std_ok,
        "path_1600": path_1600,
        "path_800": path_800,
        "orig_im": im,
        "crop_im": out_1600,
    }
    return result


def print_table(results):
    header = f"{'slug':<34} {'content box (l,t,r,b)':<26} {'crop box (l,t,r,b)':<26} {'kept%':>7} {'edge std':>9}  flags"
    print(header)
    print("-" * len(header))
    for r in results:
        cb = r["raw_box"]
        crb = r["crop_box"]
        cb_s = f"{cb[0]},{cb[1]},{cb[2]},{cb[3]}"
        crb_s = f"{crb[0]},{crb[1]},{crb[2]},{crb[3]}"
        kept_pct = r["kept_frac"] * 100
        flags = []
        if not r["kept_ok"]:
            flags.append("LOW-KEEP")
        if not r["std_ok"]:
            flags.append("FLAT-EDGE")
        flag_s = ",".join(flags) if flags else "ok"
        print(f"{r['slug']:<34} {cb_s:<26} {crb_s:<26} {kept_pct:>6.1f}% {r['edge_std']:>9.1f}  {flag_s}")


def build_contact_sheet(results, path):
    cell_w = 400
    label_h = 26
    pad = 12
    cols = 2  # 2 items per row, each item = original + trimmed side by side
    item_w = cell_w * 2 + pad
    item_h = None  # computed per row from max aspect, use fixed cell height instead

    # fixed cell height based on 16:9 for trimmed, and native ratio for original;
    # use one fixed image height so rows line up cleanly.
    cell_h = int(round(cell_w * 9 / 16))

    rows = (len(results) + cols - 1) // cols
    sheet_w = cols * item_w + pad
    sheet_h = rows * (cell_h + label_h + pad) + pad

    sheet = Image.new("RGB", (sheet_w, sheet_h), (245, 240, 230))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()

    for i, r in enumerate(results):
        row = i // cols
        col = i % cols
        x0 = pad + col * item_w
        y0 = pad + row * (cell_h + label_h + pad)

        orig = r["orig_im"]
        ow, oh = orig.size
        oh_scaled = int(round(cell_w * oh / ow))
        orig_thumb = orig.resize((cell_w, oh_scaled), Image.LANCZOS)
        # center vertically within cell_h band
        oy = y0 + label_h + max(0, (cell_h - oh_scaled) // 2)
        sheet.paste(orig_thumb, (x0, oy))

        trim_thumb = r["crop_im"].resize((cell_w, cell_h), Image.LANCZOS)
        sheet.paste(trim_thumb, (x0 + cell_w + pad, y0 + label_h))

        draw.text((x0, y0), f"{r['slug']}  (orig | trimmed)", fill=(30, 24, 16), font=font)

    sheet.save(path, "PNG")


def main():
    jobs = [(s, False) for s in FABLEWICK_SLUGS] + [(s, True) for s in RAMKABIR_SLUGS]
    results = []
    for slug, is_ramkabir in jobs:
        r = process_one(slug, is_ramkabir)
        results.append(r)

    print_table(results)

    os.makedirs(os.path.dirname(SHEET_PATH), exist_ok=True)
    build_contact_sheet(results, SHEET_PATH)
    print(f"\ncontact sheet: {SHEET_PATH}")

    failed = [r["slug"] for r in results if not (r["kept_ok"] and r["std_ok"])]
    if failed:
        print(f"\nFLAGGED (needs a look): {', '.join(failed)}")
    else:
        print("\nAll 16 covers passed both sanity checks.")


if __name__ == "__main__":
    main()
