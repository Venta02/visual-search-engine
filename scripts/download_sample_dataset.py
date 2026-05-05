"""Download a small sample dataset for testing the index.

Uses a few public domain images from Unsplash. Replace with your own
dataset for serious experiments.

Usage:
    python scripts/download_sample_dataset.py
"""

from pathlib import Path

import click
import requests
from tqdm import tqdm

# Small set of CC0 / public domain images for smoke testing.
SAMPLE_URLS = [
    "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=800",  # cat
    "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=800",     # dog
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800",  # landscape
    "https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=800",  # forest
    "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?w=800",  # mountain
    "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=800",  # cat 2
    "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=800",  # dog 2
    "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800",  # forest 2
    "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=800",  # mountain 2
    "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800",  # field
]


@click.command()
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default="data/raw/sample",
    help="Directory to save downloaded images.",
)
def main(output_dir: Path):
    """Download a small sample of test images."""
    output_dir.mkdir(parents=True, exist_ok=True)
    click.echo(f"Downloading {len(SAMPLE_URLS)} images to {output_dir}")

    for i, url in enumerate(tqdm(SAMPLE_URLS)):
        path = output_dir / f"sample_{i:03d}.jpg"
        if path.exists():
            continue
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            path.write_bytes(response.content)
        except requests.exceptions.RequestException as e:
            click.echo(f"Failed to download {url}: {e}", err=True)

    click.echo(f"Done. Files saved to {output_dir}")


if __name__ == "__main__":
    main()
