"""Prepare source photo for clean, high-fidelity ASCII portrait generation."""

from __future__ import annotations

from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "source-photo.jpg"
SOURCE_CANDIDATES = (
    SOURCE_PATH,
    ROOT / "source-photo.jpg.jpeg",
    ROOT / "source-photo.jpeg",
    ROOT / "source-photo.png",
)
PREPPED_PATH = ROOT / "source-photo-prepped.png"


def find_source_photo() -> Path | None:
    """Return the first supported source photo path without modifying it."""
    for candidate in SOURCE_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def prepare_photo(source: Path | None = None, output: Path = PREPPED_PATH) -> Path | None:
    """Crop, isolate subject from background, and enhance facial features."""
    source = source or find_source_photo()
    if source is None:
        return None

    src = Image.open(source).convert("RGB")
    w, h = src.size

    # Crop tightly centered around head, shoulders, and upper torso
    crop_left = int(w * 0.25)
    crop_right = int(w * 0.75)
    crop_top = int(h * 0.05)
    crop_bottom = int(h * 0.61)

    crop_img = src.crop((crop_left, crop_top, crop_right, crop_bottom))
    cw, ch = crop_img.size
    rgb = np.array(crop_img, dtype=float)
    gray = np.array(crop_img.convert("L"), dtype=float)

    Y, X = np.ogrid[:ch, :cw]

    # 1. Head ROI
    head_dist = ((X - 0.52 * cw) / (0.27 * cw)) ** 2 + ((Y - 0.26 * ch) / (0.25 * ch)) ** 2
    in_head = head_dist <= 1.0

    # 2. Torso ROI (tailored to actual body silhouette)
    rel_y = np.clip((Y - 0.44 * ch) / (0.56 * ch), 0, 1)
    torso_center = (0.50 - 0.02 * rel_y) * cw
    torso_half_width = (0.26 + 0.13 * rel_y) * cw
    in_torso = (Y >= 0.44 * ch) & (np.abs(X - torso_center) <= torso_half_width)

    subject_roi = in_head | in_torso

    # 3. Clean background mask
    mask = subject_roi.astype(float)
    bg_like = (gray > 175) & ((Y < 0.42 * ch) | (X > 0.78 * cw) | (X < 0.18 * cw))
    mask[bg_like] = 0.0
    mask[~subject_roi] = 0.0

    # Smooth the mask boundary with Pillow GaussianBlur for natural edge transitions
    mask_pil = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.0))
    mask = np.array(mask_pil, dtype=float) / 255.0
    mask[~subject_roi] = 0.0

    # 4. Feature and local contrast enhancement
    gray_pil = Image.fromarray(gray.astype(np.uint8))
    # Unsharp mask to emphasize glasses, eyes, nose, lips, hair, and shirt checks
    sharp_pil = gray_pil.filter(ImageFilter.UnsharpMask(radius=2.0, percent=170, threshold=2))
    sharp = np.array(sharp_pil, dtype=float)

    # Normalize subject tones
    subj_pixels = sharp[mask > 0.4]
    if len(subj_pixels) == 0:
        p_low, p_high = 0.0, 255.0
    else:
        p_low = np.percentile(subj_pixels, 2)
        p_high = np.percentile(subj_pixels, 98)
    norm = np.clip((sharp - p_low) / (p_high - p_low + 1e-5) * 255.0, 0, 255)

    # Merge subject onto pure white background (255)
    prepped = norm * mask + 255.0 * (1.0 - mask)
    prepped_pil = Image.fromarray(prepped.astype(np.uint8))

    output.parent.mkdir(parents=True, exist_ok=True)
    prepped_pil.save(output)
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
