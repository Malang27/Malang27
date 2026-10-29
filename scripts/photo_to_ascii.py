"""Convert a photo into monochrome ASCII art in data/ascii.txt (needs Pillow).

    pip install pillow
    python scripts/photo_to_ascii.py ma-photo.jpg [--cols 90] [--invert]

Works best with a portrait on a plain dark background (or with the background
removed beforehand, e.g. with remove.bg or rembg). The card is dark, so bright
pixels get dense glyphs; pass --invert for a photo on a light background.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageOps

OUT = Path(__file__).resolve().parent.parent / "data" / "ascii.txt"
RAMP = " .`:-=+*cs#%@"  # sparse -> dense


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("--cols", type=int, default=90)
    ap.add_argument("--invert", action="store_true")
    args = ap.parse_args()

    img = ImageOps.exif_transpose(Image.open(args.photo)).convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageOps.equalize(img)
    if args.invert:
        img = ImageOps.invert(img)
    # characters are ~2x taller than wide
    rows = round(args.cols * img.height / img.width * 0.5)
    img = img.resize((args.cols, rows), Image.LANCZOS)

    px = img.load()
    lines = [
        "".join(RAMP[px[x, y] * (len(RAMP) - 1) // 255] for x in range(args.cols)).rstrip()
        for y in range(rows)
    ]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(OUT.parent.parent)} ({args.cols}x{rows})")


if __name__ == "__main__":
    main()
