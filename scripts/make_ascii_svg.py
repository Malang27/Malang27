"""Render data/ascii.txt as an SVG that types itself in row by row (SMIL)."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "ascii.txt"
OUT = ROOT / "ascii-portrait.svg"
STATIC = os.environ.get("STATIC") == "1"

W, H, PAD = 370, 420, 18
BG, FG, CURSOR = "#0d1117", "#c9d1d9", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
ROW_TIME = 0.09  # seconds per row


def main():
    lines = SRC.read_text(encoding="utf-8").rstrip("\n").split("\n")
    cols = max(len(l) for l in lines)
    inner_w, inner_h = W - 2 * PAD, H - 2 * PAD
    # fit the grid: monospace glyphs are ~0.6em wide, rows use 1.15em line height
    fs = min(inner_w / (cols * 0.6), inner_h / (len(lines) * 1.15))
    lh = fs * 1.15
    text_w = cols * fs * 0.6
    x0 = (W - text_w) / 2
    y0 = (H - len(lines) * lh) / 2

    defs, rows = [], []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        top = y0 + i * lh
        body = escape(line.ljust(cols).replace(" ", " "))
        text = (f'<text x="{x0:.1f}" y="{top + fs:.1f}" textLength="{text_w:.1f}" '
                f'lengthAdjust="spacing">{body}</text>')
        if STATIC:
            rows.append(text)
            continue
        begin = f"{i * ROW_TIME:.2f}s"
        defs.append(
            f'<clipPath id="r{i}"><rect x="{x0:.1f}" y="{top:.1f}" width="0" height="{lh + 1:.1f}">'
            f'<animate attributeName="width" from="0" to="{text_w:.1f}" begin="{begin}" '
            f'dur="{ROW_TIME * 2.5:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        rows.append(
            f'<g clip-path="url(#r{i})">{text}</g>'
            f'<rect x="{x0:.1f}" y="{top + 1:.1f}" width="{fs * 0.6:.1f}" height="{lh - 1:.1f}" '
            f'fill="{CURSOR}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{begin}"/>'
            f'<animate attributeName="x" from="{x0:.1f}" to="{x0 + text_w:.1f}" begin="{begin}" '
            f'dur="{ROW_TIME * 2.5:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{i * ROW_TIME + ROW_TIME * 2.5:.2f}s"/></rect>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>text{{font-family:{FONT};font-size:{fs:.2f}px;fill:{FG}}}</style>
<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="#30363d"/>
<defs>{"".join(defs)}</defs>
{"".join(rows)}
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.name} ({cols}x{len(lines)} @ {fs:.1f}px)")


if __name__ == "__main__":
    main()
