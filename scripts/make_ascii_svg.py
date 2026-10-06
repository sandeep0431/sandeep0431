"""Generate an animated, high-fidelity ASCII portrait SVG from source photo."""

from __future__ import annotations

from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET
import numpy as np

from prep_photo import PREPPED_PATH, find_source_photo, prepare_photo

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "assets" / "sandeep-ascii.svg"

WIDTH = 68
CHAR_ASPECT = 0.52
RAMP = "  .:;=+*#%@"
GAMMA = 0.90


def _placeholder_svg() -> str:
    width = 440
    height = 520
    lines = [
        "source-photo.jpg missing",
        "",
        "Place your own photo at repo root:",
        "./source-photo.jpg",
        "",
        "Then run:",
        "python scripts/generate_all.py",
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">ASCII portrait placeholder</title>',
        '<desc id="desc">A placeholder shown until source-photo.jpg is supplied.</desc>',
        "<style>",
        ".panel{fill:#0d1117;stroke:#30363d;stroke-width:1}.bar{fill:#161b22}.dot-red{fill:#ff5f56}.dot-yellow{fill:#ffbd2e}.dot-green{fill:#27c93f}.prompt{fill:#58a6ff;font:600 13px ui-monospace,SFMono-Regular,Consolas,monospace}.text{fill:#c9d1d9;font:13px ui-monospace,SFMono-Regular,Consolas,monospace}.accent{fill:#7ee787}.row{opacity:0;animation:lineIn .5s ease forwards}@keyframes lineIn{to{opacity:1}}@media (prefers-reduced-motion: reduce){.row{animation:none;opacity:1}}",
        "</style>",
        f'<rect class="panel" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10"/>',
        f'<rect class="bar" x="1" y="1" width="{width - 2}" height="36" rx="10"/>',
        '<circle class="dot-red" cx="20" cy="18" r="5"/><circle class="dot-yellow" cx="36" cy="18" r="5"/><circle class="dot-green" cx="52" cy="18" r="5"/>',
        '<text class="prompt" x="20" y="62">sandeep@github ~ $ ./portrait --ascii</text>',
    ]
    y = 110
    for index, line in enumerate(lines):
        klass = "text accent" if "source-photo" in line or line.startswith("python") else "text"
        parts.append(f'<text class="row {klass}" x="28" y="{y + index * 26}" style="animation-delay:{0.18 + index * 0.12:.2f}s">{escape(line)}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _image_to_rows() -> list[str] | None:
    source = find_source_photo()
    if source is None:
        return None
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required for ASCII portrait generation. Install scripts/requirements-local.txt.") from exc

    prepared = prepare_photo() or PREPPED_PATH
    if not prepared.exists():
        return None

    image = Image.open(prepared).convert("L")
    aspect = image.height / image.width
    height = int(WIDTH * aspect * CHAR_ASPECT)
    small = image.resize((WIDTH, height), Image.Resampling.LANCZOS)
    arr = np.array(small, dtype=float)

    # Invert tone: dark facial features -> high character density
    val = 255.0 - arr
    val[arr >= 244] = 0

    # Gamma tone curve for smooth natural skin & hair gradations
    val = 255.0 * ((np.clip(val, 0, 255) / 255.0) ** GAMMA)

    scale = len(RAMP) - 1
    lines: list[str] = []
    for r in range(height):
        chars: list[str] = []
        for c in range(WIDTH):
            v = val[r, c]
            if v <= 4:
                chars.append(" ")
            else:
                idx = int(np.clip(v / 255.0 * scale, 0, scale))
                chars.append(RAMP[idx])
        lines.append("".join(chars).rstrip())

    # Trim empty lines at start and end
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    return lines


def build_svg() -> str:
    rows = _image_to_rows()
    if rows is None:
        return _placeholder_svg()

    max_line_len = max((len(r) for r in rows), default=WIDTH)
    char_width = 7.0
    line_height = 9.2
    
    pad_x = 22
    pad_top = 70
    pad_bottom = 22
    width = int(max(max_line_len * char_width + pad_x * 2, 420))
    height = int(len(rows) * line_height + pad_top + pad_bottom)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Animated ASCII portrait for Sandeep Kumar Sahu</title>',
        '<desc id="desc">Character-based terminal portrait generated from source photo.</desc>',
        "<style>",
        ".panel{fill:#0d1117;stroke:#30363d;stroke-width:1}.bar{fill:#161b22}.dot-red{fill:#ff5f56}.dot-yellow{fill:#ffbd2e}.dot-green{fill:#27c93f}.prompt{fill:#58a6ff;font:600 13px ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace}.title{fill:#8b949e;font:11px ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace}.ascii{fill:#7ee787;font:8.5px ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace;white-space:pre}.row{opacity:0;animation:scan .4s ease forwards}@keyframes scan{from{opacity:0;transform:translateY(2px)}to{opacity:1;transform:translateY(0)}}@media (prefers-reduced-motion: reduce){.row{animation:none;opacity:1}}",
        "</style>",
        f'<rect class="panel" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8"/>',
        f'<rect class="bar" x="1" y="1" width="{width - 2}" height="32" rx="8"/>',
        '<circle class="dot-red" cx="18" cy="16" r="4.5"/><circle class="dot-yellow" cx="32" cy="16" r="4.5"/><circle class="dot-green" cx="46" cy="16" r="4.5"/>',
        f'<text class="title" x="{width // 2}" y="20" text-anchor="middle">sandeep@github: ~/portrait</text>',
        '<text class="prompt" x="20" y="52">sandeep@github ~ $ ./portrait --ascii</text>',
    ]
    for index, row in enumerate(rows):
        delay = min(0.08 + index * 0.024, 1.4)
        y = pad_top + index * line_height
        parts.append(f'<text class="ascii row" x="{pad_x}" y="{y:.1f}" style="animation-delay:{delay:.3f}s">{escape(row)}</text>')
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
