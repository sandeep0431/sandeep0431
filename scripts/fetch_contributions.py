"""Fetch public GitHub contribution calendar data for the profile README."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from html import unescape
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_PATH = DATA_DIR / "contributions.json"
USERNAME = "sandeep0431"
PROFILE_URL = f"https://github.com/users/{USERNAME}/contributions"


@dataclass(frozen=True)
class ContributionDay:
    date: str
    count: int
    level: int


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


def _empty_calendar(reason: str) -> dict:
    """Return a full one-year calendar with explicit warning metadata."""
    end = _today_utc()
    start = end - timedelta(days=364)
    days: list[ContributionDay] = []
    current = start
    while current <= end:
        days.append(ContributionDay(current.isoformat(), 0, 0))
        current += timedelta(days=1)
    return {
        "username": USERNAME,
        "source": "fallback-zero-calendar",
        "source_url": PROFILE_URL,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "warnings": [reason],
        "days": [asdict(day) for day in days],
    }


def _fetch_html() -> str:
    headers = {
        "User-Agent": "sandeep0431-profile-readme-generator/1.0",
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        import requests

        response = requests.get(PROFILE_URL, headers=headers, timeout=20)
        if response.status_code == 429:
            raise RuntimeError("GitHub rate limit returned HTTP 429.")
        response.raise_for_status()
        return response.text
    except ImportError:
        from urllib.request import Request, urlopen

        request = Request(PROFILE_URL, headers=headers)
        with urlopen(request, timeout=20) as response:  # nosec: public GitHub URL
            status = getattr(response, "status", 200)
            if status >= 400:
                raise RuntimeError(f"GitHub returned HTTP {status}.")
            return response.read().decode("utf-8", errors="replace")


def _level_from_count(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    return 4


def _parse_with_bs4(html: str) -> list[ContributionDay]:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    soup = BeautifulSoup(html, "html.parser")
    days: list[ContributionDay] = []
    seen: set[str] = set()
    for element in soup.select("[data-date]"):
        day = element.get("data-date", "").strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day) or day in seen:
            continue
        raw_count = element.get("data-count") or element.get("data-level") or "0"
        count_match = re.search(r"\d+", raw_count)
        count = int(count_match.group(0)) if count_match else 0
        raw_level = element.get("data-level")
        level = int(raw_level) if raw_level and raw_level.isdigit() else _level_from_count(count)
        days.append(ContributionDay(day, count, max(0, min(level, 4))))
        seen.add(day)
    return days


def _parse_with_regex(html: str) -> list[ContributionDay]:
    pattern = re.compile(
        r'data-date="(?P<date>\d{4}-\d{2}-\d{2})"[^>]*(?:data-count="(?P<count>\d+)")?[^>]*(?:data-level="(?P<level>\d+)")?',
        re.IGNORECASE,
    )
    days: list[ContributionDay] = []
    seen: set[str] = set()
    for match in pattern.finditer(unescape(html)):
        day = match.group("date")
        if day in seen:
            continue
        count = int(match.group("count") or 0)
        level = int(match.group("level") or _level_from_count(count))
        days.append(ContributionDay(day, count, max(0, min(level, 4))))
        seen.add(day)
    return days


def _normalize_days(days: Iterable[ContributionDay]) -> list[ContributionDay]:
    by_date = {item.date: item for item in days}
    end = _today_utc()
    start = end - timedelta(days=364)
    normalized: list[ContributionDay] = []
    current = start
    while current <= end:
        key = current.isoformat()
        normalized.append(by_date.get(key, ContributionDay(key, 0, 0)))
        current += timedelta(days=1)
    return normalized


def fetch_contributions() -> dict:
    """Fetch and normalize approximately one year of contribution data."""
    try:
        html = _fetch_html()
        parsed = _parse_with_bs4(html) or _parse_with_regex(html)
        if not parsed:
            raise RuntimeError("No contribution cells with data-date were found in GitHub HTML.")
        days = _normalize_days(parsed)
        return {
            "username": USERNAME,
            "source": "github-public-html",
            "source_url": PROFILE_URL,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "warnings": [],
            "days": [asdict(day) for day in days],
        }
    except Exception as exc:  # noqa: BLE001 - user-facing fallback should catch all fetch/parser errors.
        return _empty_calendar(f"Contribution fetch fell back to a zero calendar: {exc}")


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = fetch_contributions()
    if not payload.get("days"):
        raise RuntimeError("Refusing to write an empty contribution calendar.")
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    warnings = payload.get("warnings", [])
    if warnings:
        print("Wrote fallback contribution data:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print(f"Wrote contribution data for {USERNAME} to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
