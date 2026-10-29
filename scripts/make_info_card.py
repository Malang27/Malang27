"""Hand-authored neofetch-style info card that prints itself line by line."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

W, H = 490, 420
BG, FG, MUTED, KEY = "#0d1117", "#c9d1d9", "#8b949e", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

TITLE = "malang@github"
ROWS = [
    ("Rôle", "DevOps & Fullstack Engineer"),
    ("Actuel", "Tiak-Tiak × Talent 2 Africa"),
    ("Avant", "Zone01 Dakar / Atos Sénégal"),
    ("Lieu", "Dakar, Sénégal"),
    ("Diplôme", "Master Systèmes & Réseaux"),
    (None, None),
    ("Langages", "Go · TypeScript · Python · Java · Rust"),
    ("Front", "React · Angular · Flutter"),
    ("Back", "Go · Spring Boot · PostgreSQL"),
    ("DevOps", "Docker · AWS · GitHub Actions · Linux"),
    (None, None),
    ("Impact", "−45 % de temps de requête (PostgreSQL)"),
    ("", "99,9 % de disponibilité en production"),
    ("", "déploiements 40 % plus rapides"),
    ("Temps réel", "100+ joueurs, latence < 50 ms"),
    (None, None),
    ("Contact", "mvlang27@gmail.com"),
]
SWATCHES = ["#ff5f56", "#ffbd2e", "#27c93f", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]


def main():
    x, y, lh = 24, 64, 18
    lines = [
        f'<text x="{x}" y="{y - 22}" class="t"><tspan fill="{KEY}" font-weight="bold">{TITLE}</tspan></text>',
        f'<text x="{x}" y="{y - 6}" class="t m">{"-" * len(TITLE)}</text>',
    ]
    for i, (k, v) in enumerate(ROWS):
        if k is None:
            continue
        key = f'<tspan fill="{KEY}" font-weight="bold">{escape(k)}</tspan>' if k else ""
        lines.append(
            f'<text x="{x}" y="{y + 10 + i * lh}" class="t l" style="animation-delay:{0.25 + i * 0.12:.2f}s">'
            f'{key}<tspan x="{x + 96}">{escape(v)}</tspan></text>'
        )
    sy = y + 10 + len(ROWS) * lh + 8
    swatches = "".join(
        f'<rect x="{x + i * 26}" y="{sy}" width="22" height="12" rx="2" fill="{c}" class="l" '
        f'style="animation-delay:{0.25 + len(ROWS) * 0.12:.2f}s"/>'
        for i, c in enumerate(SWATCHES)
    )

    css = "" if STATIC else (
        ".l{opacity:0;animation:in .45s ease-out forwards}"
        "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}"
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>.t{{font-family:{FONT};font-size:12.5px;fill:{FG}}}.m{{fill:{MUTED}}}{css}</style>
<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="#30363d"/>
{"".join(lines)}
{swatches}
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
