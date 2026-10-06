"""Generate an animated ASCII portrait SVG from source-photo.jpg."""

from __future__ import annotations

from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

from prep_photo import PREPPED_PATH, find_source_photo, prepare_photo

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "assets" / "sandeep-ascii.svg"

WIDTH = 70
CHARSET = " .,:;irsXA253hMHGS#9B&@"
FONT_SIZE = 7
LINE_HEIGHT = 7.8
CONTRAST = 1.35
BRIGHTNESS = 1.04
INVERT = True


def _placeholder_svg() -> str:
    width = 430
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
        ".panel{fill:#0d1117;stroke:#30363d;stroke-width:1}.prompt{fill:#58a6ff;font:600 15px ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace}.text{fill:#c9d1d9;font:14px ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace}.accent{fill:#7ee787}.row{opacity:0;animation:lineIn .5s ease forwards}@keyframes lineIn{to{opacity:1}}@media (prefers-reduced-motion: reduce){.row{animation:none;opacity:1}}",
        "</style>",
        f'<rect class="panel" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8"/>',
        '<text class="prompt" x="24" y="38">sandeep@github ~ $ ./render_portrait.sh</text>',
    ]
    y = 108
    for index, line in enumerate(lines):
        klass = "text accent" if "source-photo" in line or line.startswith("python") else "text"
        parts.append(f'<text class="row {klass}" x="36" y="{y + index * 28}" style="animation-delay:{0.18 + index * 0.12:.2f}s">{escape(line)}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _image_to_rows() -> list[str] | None:
    source = find_source_photo()
    if source is None:
        return None
    try:
        from PIL import Image, ImageEnhance, ImageOps
    except ImportError as exc:
        raise RuntimeError("Pillow is required for ASCII portrait generation. Install scripts/requirements-local.txt.") from exc

    prepared = prepare_photo() or PREPPED_PATH
    image = Image.open(prepared).convert("L")
    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Contrast(image).enhance(CONTRAST)
    image = ImageEnhance.Brightness(image).enhance(BRIGHTNESS)
    aspect = image.height / image.width
    rows = max(52, int(WIDTH * aspect * 0.54))
    image = image.resize((WIDTH, rows))
    flat_data = getattr(image, "get_flattened_data", None)
    pixels = list(flat_data() if flat_data else image.getdata())
    chars: list[str] = []
    scale = len(CHARSET) - 1
    for pixel in pixels:
        value = 255 - pixel if INVERT else pixel
        chars.append(CHARSET[min(scale, max(0, int(value / 255 * scale)))])
    return ["".join(chars[i : i + WIDTH]).rstrip() for i in range(0, len(chars), WIDTH)]


def build_svg() -> str:
    rows = _image_to_rows()
    if rows is None:
        return _placeholder_svg()

    width = int(WIDTH * FONT_SIZE * 0.64 + 48)
    height = int(len(rows) * LINE_HEIGHT + 84)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Animated ASCII portrait for Sandeep Kumar Sahu</title>',
        '<desc id="desc">A character-based portrait generated from source-photo.jpg.</desc>',
        "<style>",
        ".panel{fill:#0d1117;stroke:#30363d;stroke-width:1}.prompt{fill:#58a6ff;font:600 13px ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace}.ascii{fill:#7ee787;font:8px ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace;white-space:pre}.row{opacity:0;animation:scan .45s ease forwards}@keyframes scan{from{opacity:0;transform:translateY(3px)}to{opacity:1;transform:translateY(0)}}@media (prefers-reduced-motion: reduce){.row{animation:none;opacity:1}}",
        "</style>",
        f'<rect class="panel" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8"/>',
        '<text class="prompt" x="20" y="30">sandeep@github ~ $ ./portrait --ascii</text>',
    ]
    top = 58
    for index, row in enumerate(rows):
        delay = min(0.1 + index * 0.026, 1.5)
        parts.append(f'<text class="ascii row" x="20" y="{top + index * LINE_HEIGHT:.1f}" style="animation-delay:{delay:.3f}s">{escape(row)}</text>')
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
