"""Run all local generators in the correct order."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _run(script_name: str) -> None:
    script = SCRIPTS / script_name
    print(f"\n$ {sys.executable} {script.relative_to(ROOT)}")
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)


def main() -> int:
    steps = [
        "fetch_contributions.py",
        "render_heatmap_svg.py",
        "make_info_card.py",
        "prep_photo.py",
        "make_ascii_svg.py",
        "make_profile_photo.py",
    ]
    for step in steps:
        _run(step)
    print("\nGenerated profile assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
