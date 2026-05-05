# Scripts

CLI utilities for one-off tasks like data download, indexing, and benchmarking.

## Available Scripts

### `download_sample_dataset.py`
Downloads a small set of public domain images for smoke testing.

```bash
python scripts/download_sample_dataset.py --output-dir data/raw/sample
```

### `build_index.py`
Indexes a directory of images into Qdrant.

```bash
python scripts/build_index.py --dataset data/raw/sample --batch-size 16
```

Options:
- `--dataset`: Path to the directory containing images (required).
- `--batch-size`: Number of images per embedding batch (default: 32).
- `--recursive` / `--no-recursive`: Recurse into subdirectories (default: yes).

## Adding a New Script

Use `click` for argument parsing. Each script should:

1. Have a docstring at the top with usage examples.
2. Use `setup_logging()` from `src.core.logging` for consistent output.
3. Be runnable as a module: `python -m scripts.your_script`.
