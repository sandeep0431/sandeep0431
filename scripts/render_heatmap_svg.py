"""Render GitHub contribution data as an animated SVG heatmap."""

from __future__ import annotations

import json
from datetime import date, datetime
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "contributions.json"
OUTPUT_PATH = ROOT / "assets" / "contrib-heatmap.svg"

COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _load_data() -> dict:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing {DATA_PATH}. Run scripts/fetch_contributions.py first.")
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    days = payload.get("days")
    if not isinstance(days, list) or not days:
        raise ValueError(f"{DATA_PATH} does not contain contribution days.")
    return payload


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"Malformed contribution date: {value}") from exc


def _weeks(days: list[dict]) -> list[list[dict | None]]:
    parsed = []
    for item in days:
        parsed.append(
            {
                "date": _parse_date(str(item["date"])),
                "count": int(item.get("count", 0)),
                "level": max(0, min(int(item.get("level", 0)), 4)),
            }
        )
    parsed.sort(key=lambda item: item["date"])
    weeks: list[list[dict | None]] = []
    current_week: list[dict | None] = [None] * 7
    for item in parsed:
        weekday = (item["date"].weekday() + 1) % 7
        if weekday == 0 and any(current_week):
            weeks.append(current_week)
            current_week = [None] * 7
        current_week[weekday] = item
    if any(current_week):
        weeks.append(current_week)
    return weeks[-53:]


def render_svg() -> str:
    payload = _load_data()
    weeks = _weeks(payload["days"])
    cell = 11
    gap = 4
    left = 44
    top = 50
    grid_width = len(weeks) * (cell + gap) - gap
    width = left + grid_width + 28
    height = top + 7 * (cell + gap) + 48

    month_labels: list[tuple[int, str]] = []
    seen_months: set[tuple[int, int]] = set()
    for week_index, week in enumerate(weeks):
        dated = [item for item in week if item]
        if not dated:
            continue
        first = dated[0]["date"]
        key = (first.year, first.month)
        if key not in seen_months:
            seen_months.add(key)
            month_labels.append((left + week_index * (cell + gap), MONTHS[first.month - 1]))

    warning_text = "; ".join(payload.get("warnings", []))
    total = sum(int(day.get("count", 0)) for day in payload["days"])

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">Animated GitHub contribution heatmap for sandeep0431</title>",
        f"<desc id=\"desc\">One year contribution calendar with {total} public contributions. {escape(warning_text)}</desc>",
        "<style>",
        ".bg{fill:#0d1117}.panel{fill:#0d1117;stroke:#30363d;stroke-width:1}.label{fill:#8b949e;font:11px ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace}.title{fill:#c9d1d9;font:600 14px ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace}.cell{opacity:0;animation:reveal .42s ease forwards}.legend{stroke:#30363d;stroke-width:1}@keyframes reveal{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}@media (prefers-reduced-motion: reduce){.cell{animation:none;opacity:1}}",
        "</style>",
        f'<rect class="bg" width="{width}" height="{height}" rx="8"/>',
        f'<rect class="panel" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8"/>',
        '<text class="title" x="18" y="26">sandeep@github ~ $ ./contributions.sh</text>',
    ]

    for x, label in month_labels:
        parts.append(f'<text class="label" x="{x}" y="43">{label}</text>')
    for row, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        parts.append(f'<text class="label" x="18" y="{top + row * (cell + gap) + 9}">{label}</text>')

    index = 0
    for week_index, week in enumerate(weeks):
        for weekday, item in enumerate(week):
            if item is None:
                continue
            x = left + week_index * (cell + gap)
            y = top + weekday * (cell + gap)
            level = item["level"]
            count = item["count"]
            day = item["date"].isoformat()
            delay = min(index * 0.012, 1.8)
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{COLORS[level]}" style="animation-delay:{delay:.3f}s">'
                f"<title>{day}: {count} contribution{'s' if count != 1 else ''}</title></rect>"
            )
            index += 1

    legend_y = height - 24
    legend_x = width - 150
    parts.append(f'<text class="label" x="{legend_x - 36}" y="{legend_y + 9}">Less</text>')
    for i, color in enumerate(COLORS):
        parts.append(f'<rect class="legend" x="{legend_x + i * 16}" y="{legend_y}" width="11" height="11" rx="2" fill="{color}"/>')
    parts.append(f'<text class="label" x="{legend_x + 88}" y="{legend_y + 9}">More</text>')
    if warning_text:
        parts.append(f'<text class="label" x="18" y="{height - 16}">data: fallback calendar; run fetch when online</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    svg = render_svg()
    ET.fromstring(svg)
    OUTPUT_PATH.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
