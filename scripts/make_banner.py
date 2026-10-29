"""Default portrait: draws "MAL/ANG" in block letters into data/ascii.txt.

Replace it with a real portrait by running photo_to_ascii.py instead.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "ascii.txt"

FONT = {
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
}


def word(text):
    """Bitmap rows for a word, one pixel = two chars so it looks square."""
    grid = [".".join(FONT[c][r] for c in text) for r in range(7)]
    out = []
    for r, row in enumerate(grid):
        line = ""
        for c, px in enumerate(row):
            if px == "#":
                line += "@@"
            elif r and c and grid[r - 1][c - 1] == "#":
                line += "::"  # drop shadow
            else:
                line += "  "
        out.append(line)
    return out


def main():
    lines = [""] + word("MAL") + ["", ""] + word("ANG") + [""]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(OUT.parent.parent)}")


if __name__ == "__main__":
    main()
