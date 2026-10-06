"""Generate a polished real-photo portrait asset for the README."""

from __future__ import annotations

from pathlib import Path

from prep_photo import find_source_photo

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "assets" / "profile-photo.jpg"


def make_profile_photo() -> Path | None:
    """Create a clean portrait crop without modifying the original photo."""
    source = find_source_photo()
    if source is None:
        return None

    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    except ImportError as exc:
        raise RuntimeError("Pillow is required for profile photo generation. Install scripts/requirements-local.txt.") from exc

    image = Image.open(source).convert("RGB")
    width, height = image.size

    # Perfectly centered crop focusing on face, shoulders, and chest
    crop_width = int(width * 0.66)
    crop_height = int(crop_width * 1.22)
    left = int((width - crop_width) * 0.48)
    top = int(height * 0.03)
    right = min(width, left + crop_width)
    bottom = min(height, top + crop_height)
    if bottom - top < crop_height:
        top = max(0, bottom - crop_height)
    if right - left < crop_width:
        left = max(0, right - crop_width)

    image = image.crop((left, top, right, bottom))
    image = ImageOps.autocontrast(image, cutoff=0.5)
    image = ImageEnhance.Color(image).enhance(1.06)
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = ImageEnhance.Sharpness(image).enhance(1.15)
    image = image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=85, threshold=3))
    image.thumbnail((760, 920), Image.Resampling.LANCZOS)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT_PATH, quality=94, optimize=True, progressive=True)
    return OUTPUT_PATH


def main() -> int:
    result = make_profile_photo()
    if result is None:
        print("No source photo found; skipped profile-photo.jpg generation.")
        return 0
    print(f"Wrote {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
