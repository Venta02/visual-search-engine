"""Image-handling helpers: safe loading, hashing for cache keys."""

import hashlib
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def load_image_safely(path: str | Path) -> Image.Image | None:
    """Load an image, returning None on any read failure.

    Args:
        path: Path to the image file.

    Returns:
        A PIL Image in RGB mode, or None if loading failed.
    """
    try:
        image = Image.open(path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image
    except (UnidentifiedImageError, OSError, FileNotFoundError):
        return None


def hash_image_bytes(image_bytes: bytes) -> str:
    """Compute a stable SHA-256 hash of image bytes.

    Used as a cache key for image embeddings so that the same image
    uploaded twice does not get re-embedded.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        Hex-encoded SHA-256 digest.
    """
    return hashlib.sha256(image_bytes).hexdigest()
