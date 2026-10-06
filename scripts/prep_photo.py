"""Prepare source-photo.jpg for ASCII portrait generation."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "source-photo.jpg"
SOURCE_CANDIDATES = (
    SOURCE_PATH,
    ROOT / "source-photo.jpeg",
    ROOT / "source-photo.jpg.jpeg",
)
PREPPED_PATH = ROOT / "source-photo-prepped.png"


def find_source_photo() -> Path | None:
    """Return the first supported source photo path without modifying it."""
    for candidate in SOURCE_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def prepare_photo(source: Path | None = None, output: Path = PREPPED_PATH) -> Path | None:
    """Crop, enhance, and save a local photo if Pillow is available."""
    source = source or find_source_photo()
    if source is None:
        return None
    try:
        from PIL import Image, ImageEnhance, ImageOps
    except ImportError as exc:
        raise RuntimeError("Pillow is required for portrait generation. Install scripts/requirements-local.txt.") from exc

    image = Image.open(source).convert("RGB")
    width, height = image.size
    # GitHub README portraits read best when the face and shoulders dominate
    # the frame. This keeps the original untouched and writes only a prepped PNG.
    target_ratio = 0.78
    crop_height = int(height * 0.62)
    crop_width = min(width, int(crop_height * target_ratio))
    top = int(height * 0.03)
    left = max(0, int((width - crop_width) * 0.58))
    right = min(width, left + crop_width)
    bottom = min(height, top + crop_height)
    if right - left < crop_width:
        left = max(0, right - crop_width)
    image = image.crop((left, top, right, bottom))

    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Contrast(image).enhance(1.35)
    image = ImageEnhance.Brightness(image).enhance(1.04)
    image.save(output)
    return output


def main() -> int:
    result = prepare_photo()
    if result is None:
        print(f"No {SOURCE_PATH.name} found; portrait generator will create a placeholder.")
        return 0
    print(f"Wrote {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
