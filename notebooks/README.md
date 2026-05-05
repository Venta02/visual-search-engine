# Notebooks

Exploratory scripts written as VS Code Interactive Python files. Each `# %%` marker defines a cell that can be run independently with the VS Code Python and Jupyter extensions.

## Why `.py` Instead of `.ipynb`

- **Better version control.** Git diffs are readable on `.py` files. Notebook JSON is not.
- **Easier code review.** Reviewers see real code, not embedded outputs and metadata.
- **Cleaner refactoring.** Move a function from a `.py` notebook into the main codebase by copy-paste, no conversion step needed.
- **Linting works.** `ruff` and `black` lint these files like any other Python file.

The trade-off is you lose persistent inline outputs. For exploration this is acceptable. For final reports, export to HTML or save figures as PNG.

## Required VS Code Extensions

Install these from the VS Code marketplace:
- **Python** (Microsoft, free)
- **Jupyter** (Microsoft, free) - lets you run `# %%` cells

## How to Run

1. Open any file in this directory.
2. Click "Run Cell" above any `# %%` marker, or press `Shift + Enter` while inside a cell.
3. Output appears in the Interactive Window panel.
4. Variables persist between cell runs in the same session.

## Available Notebooks

### `01_explore_siglip.py`
Walk through the SigLIP embedding model: load it, embed text and images, verify normalization, and compute cross-modal similarity. Start here if you have never used SigLIP before.

### `02_visualize_embeddings.py`
Project 768-dimensional embeddings down to 2D using UMAP (or PCA if UMAP is not installed). Verifies that semantically similar concepts cluster together. Great visualization for portfolio blog posts.

Requires `pip install umap-learn` for the UMAP path.

### `03_benchmark_latency.py`
Measure embedding latency for single calls and various batch sizes. Generates plots and saves results to `docs/benchmarks/embedding_latency.csv`. Use this to fill in the benchmark numbers in the main README.

## Adding Your Own Notebook

Naming convention: `NN_short_description.py` where NN is a two-digit sequence number.

Structure each notebook like a tutorial:
1. Top-level docstring explaining what it covers.
2. `# %% [markdown]` cells for narrative.
3. `# %%` cells for code.
4. End with a "What to try next" section.

Keep notebooks under 200 lines. If a notebook grows beyond that, refactor the reusable parts into `src/` modules.

## What Notebooks Are NOT For

- Production code. If you write a useful function in a notebook, move it into `src/`.
- Persistent state. Re-run cells from the top after restarting the kernel.
- Tests. Use `pytest` files in `tests/` instead.
