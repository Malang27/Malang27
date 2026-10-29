"""Convert a photo into monochrome ASCII art in data/ascii.txt (needs Pillow + numpy).

    pip install pillow numpy
    python scripts/photo_to_ascii.py ma-photo.jpg [--cols 80] [--crop 0.05 0.72] [--crop-x 0.1 0.9]

A plain, light studio background is removed by flood-filling from the image
borders, so only the subject prints. The card is dark, so bright pixels get
dense glyphs (the portrait reads like a light-on-dark photo).
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

OUT = Path(__file__).resolve().parent.parent / "data" / "ascii.txt"
RAMP = " .`:-=+*cs#%@"  # sparse -> dense; space is reserved for the background


def subject_mask(gray, threshold):
    """True where the subject is.

    Pixels brighter than `threshold` are background candidates; only those
    connected to the top/left/right borders count, so highlights inside the
    face survive. The mask is then eroded to drop the bright halo on edges.
    """
    probe = gray.filter(ImageFilter.GaussianBlur(2)).point(lambda v: 255 if v >= threshold else 0)
    w, h = probe.size
    seeds = [(x, 0) for x in range(0, w, 4)] + [(0, y) for y in range(0, h, 4)] + \
            [(w - 1, y) for y in range(0, h, 4)]
    for seed in seeds:
        if probe.getpixel(seed) == 255:
            ImageDraw.floodfill(probe, seed, 128)
    subject = probe.point(lambda v: 0 if v == 128 else 255)
    return np.asarray(subject.filter(ImageFilter.MinFilter(7))) > 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("--cols", type=int, default=80)
    ap.add_argument("--crop", type=float, nargs=2, default=(0.0, 1.0), metavar=("TOP", "BOTTOM"),
                    help="vertical crop as fractions of the height")
    ap.add_argument("--crop-x", type=float, nargs=2, default=(0.0, 1.0), metavar=("LEFT", "RIGHT"),
                    help="horizontal crop as fractions of the width")
    ap.add_argument("--threshold", type=int, default=150,
                    help="background is brighter than this (0-255)")
    args = ap.parse_args()

    img = ImageOps.exif_transpose(Image.open(args.photo)).convert("L")
    top, bottom = (round(f * img.height) for f in args.crop)
    left, right = (round(f * img.width) for f in args.crop_x)
    img = img.crop((left, top, right, bottom))
    mask = Image.fromarray(subject_mask(img, args.threshold).astype(np.uint8) * 255)

    # characters are ~2x taller than wide
    rows = round(args.cols * img.height / img.width * 0.5)
    size = (args.cols, rows)
    lum = np.asarray(img.resize(size, Image.LANCZOS), dtype=float)
    keep = np.asarray(mask.resize(size, Image.LANCZOS)) > 127

    # equalize over the subject only, so the background doesn't eat the contrast
    vals = lum[keep]
    ranks = np.searchsorted(np.sort(vals), lum) / max(len(vals), 1)
    idx = 1 + np.clip(ranks * (len(RAMP) - 1), 0, len(RAMP) - 2).astype(int)
    idx[~keep] = 0

    lines = ["".join(RAMP[i] for i in row).rstrip() for row in idx]
    while lines and not lines[0]:
        lines.pop(0)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(OUT.parent.parent)} ({args.cols}x{len(lines)})")


if __name__ == "__main__":
    main()
