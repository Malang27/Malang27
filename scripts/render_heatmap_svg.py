"""Render data/contributions.json as an animated, terminal-styled heatmap SVG."""
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BG, FG, MUTED = "#0d1117", "#c9d1d9", "#8b949e"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
MONTHS = "janv. févr. mars avr. mai juin juil. août sept. oct. nov. déc.".split()

W, CELL, GAP = 860, 12, 3
STEP = CELL + GAP
X0, Y0 = 52, 66


def fmt(n):
    return f"{n:,}".replace(",", " ")


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday

    rects, month_labels, last_month = [], [], None
    for i, d in enumerate(days):
        col, row = divmod(i + offset, 7)
        x, y = X0 + col * STEP, Y0 + row * STEP
        delay = (col + row) * 0.018
        anim = "" if STATIC else f' style="animation-delay:{delay:.3f}s"'
        tip = f'{d["count"]} contribution(s) le {d["date"]}'
        rects.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{PALETTE[min(d["level"], 4)]}"{anim}><title>{tip}</title></rect>'
        )
        m = d["date"][5:7]
        if row == 0 and m != last_month:
            last_month = m
            # drop a label that would collide with the previous one
            if month_labels and col - month_labels[-1][0] < 3:
                month_labels.pop()
            if col < 52:
                month_labels.append((col, f'<text x="{x}" y="{Y0 - 8}" class="t m">{MONTHS[int(m) - 1]}</text>'))

    day_labels = "".join(
        f'<text x="{X0 - 8}" y="{Y0 + r * STEP + 10}" class="t m" text-anchor="end">{lbl}</text>'
        for r, lbl in ((1, "lun"), (3, "mer"), (5, "ven"))
    )

    fy = Y0 + 7 * STEP + 28
    legend_x = W - 24 - 5 * STEP - 40
    legend = "".join(
        f'<rect x="{legend_x + 4 + i * STEP}" y="{fy - 10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    )
    best = data["best_day"]
    stats = (f'<tspan fill="#39d353">{fmt(data["total"])}</tspan> contributions sur 12 mois · '
             f'série actuelle <tspan fill="#39d353">{data["current_streak"]} j</tspan> · '
             f'record <tspan fill="#39d353">{data["longest_streak"]} j</tspan> · '
             f'meilleur jour {best["count"]} ({best["date"]})')

    h = fy + 42
    css = "" if STATIC else (
        ".c{opacity:0;transform-box:fill-box;transform-origin:center;"
        "animation:pop .4s ease-out forwards}"
        "@keyframes pop{from{opacity:0;transform:translateY(-6px) scale(.6)}"
        "to{opacity:1;transform:none}}"
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<style>.t{{font-family:{FONT};font-size:11px;fill:{FG}}}.m{{fill:{MUTED};font-size:10px}}{css}</style>
<rect width="{W}" height="{h}" rx="10" fill="{BG}" stroke="#30363d"/>
<circle cx="20" cy="18" r="5" fill="#ff5f56"/><circle cx="36" cy="18" r="5" fill="#ffbd2e"/><circle cx="52" cy="18" r="5" fill="#27c93f"/>
<text x="{W / 2}" y="22" class="t m" text-anchor="middle">{data["username"]}@github: ~/contributions</text>
{"".join(lbl for _, lbl in month_labels)}{day_labels}
{"".join(rects)}
<text x="{W / 2}" y="{fy + 24}" class="t" text-anchor="middle">{stats}</text>
<text x="{legend_x - 6}" y="{fy}" class="t m" text-anchor="end">Moins</text>{legend}
<text x="{legend_x + 8 + 5 * STEP}" y="{fy}" class="t m">Plus</text>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
