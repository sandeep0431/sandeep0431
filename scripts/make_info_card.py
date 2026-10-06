"""Generate the animated terminal info card SVG."""

from __future__ import annotations

from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "assets" / "info-card.svg"

ROWS = [
    ("USER", "Sandeep Kumar Sahu"),
    ("ROLE", "B.Tech CSE @ VSSUT"),
    ("STATUS", "4th semester completed"),
    ("CGPA", "8.63 / 10"),
    ("FOCUS", "Cybersecurity | AI/ML"),
    ("BUILD", "Web | Cloud | Automation"),
    ("STACK", "Python | TypeScript | React"),
    ("CLOUD", "AWS | Serverless"),
    ("CURRENT", "AEGIS + TabMind"),
]


def build_svg() -> str:
    width = 620
    row_height = 28
    top = 92
    height = top + len(ROWS) * row_height + 30
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Terminal profile card for Sandeep Kumar Sahu</title>',
        '<desc id="desc">Animated command output describing academic status, interests, and stack.</desc>',
        "<style>",
        ".panel{fill:#0d1117;stroke:#30363d;stroke-width:1}.bar{fill:#161b22}.dot-red{fill:#ff5f56}.dot-yellow{fill:#ffbd2e}.dot-green{fill:#27c93f}.prompt{fill:#58a6ff;font:600 15px ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace}.key{fill:#7ee787;font:700 14px ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace}.value{fill:#c9d1d9;font:14px ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace}.row{opacity:0;animation:lineIn .5s ease forwards}@keyframes lineIn{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}@media (prefers-reduced-motion: reduce){.row{animation:none;opacity:1}}",
        "</style>",
        f'<rect class="panel" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8"/>',
        f'<rect class="bar" x="1" y="1" width="{width - 2}" height="40" rx="8"/>',
        '<circle class="dot-red" cx="24" cy="21" r="6"/><circle class="dot-yellow" cx="44" cy="21" r="6"/><circle class="dot-green" cx="64" cy="21" r="6"/>',
        '<text class="prompt" x="24" y="68">sandeep@github ~ $ whoami</text>',
    ]
    for index, (key, value) in enumerate(ROWS):
        y = top + index * row_height
        delay = 0.25 + index * 0.11
        parts.append(f'<g class="row" style="animation-delay:{delay:.2f}s">')
        parts.append(f'<text class="key" x="24" y="{y}">{escape(key):<8}</text>')
        parts.append(f'<text class="value" x="128" y="{y}">{escape(value)}</text>')
        parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    svg = build_svg()
    ET.fromstring(svg)
    OUTPUT_PATH.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
