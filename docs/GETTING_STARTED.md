# Getting Started

A friendlier walkthrough than the development guide. If you are looking at this project for the first time, start here.

## What This Project Does

It is a search engine for images. You can:

1. Type a description like "a cat sitting on a windowsill" and get matching images.
2. Upload an image and get visually similar images back.

Under the hood, it uses a deep learning model (SigLIP) to convert both images and text into vectors, then finds the closest vectors in a database.

## What You Need

- A computer with at least 8 GB of RAM
- Python 3.10 or newer installed
- Docker Desktop installed and running
- Around 5 GB of free disk space (the model and dataset take space)

## Step-by-Step First Run

### 1. Get the code

```bash
git clone https://github.com/yourusername/visual-search-engine.git
cd visual-search-engine
```

### 2. Set up a Python environment

A virtual environment keeps this project's dependencies separate from your other Python projects.

```bash
python -m venv venv
source venv/bin/activate
```

On Windows, the activation command is:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

This takes a few minutes the first time because PyTorch is large.

```bash
pip install -r requirements.txt
```

### 4. Configure the environment

```bash
cp .env.example .env
```

The defaults work for local development. If you have an NVIDIA GPU, edit `.env` and change `EMBEDDING_DEVICE=cpu` to `EMBEDDING_DEVICE=cuda`.

### 5. Start the supporting services

This starts Qdrant (the vector database) and Redis (the cache) in the background.

```bash
docker compose up -d qdrant redis
```

Verify they are healthy:

```bash
curl http://localhost:6333/healthz
```

You should see `healthz check passed` or similar.

### 6. Download some sample images

```bash
python scripts/download_sample_dataset.py
```

This downloads ten public-domain images to `data/raw/sample/`.

### 7. Build the index

This is the slow part. The first run will download the SigLIP model (about 800 MB).

```bash
python scripts/build_index.py --dataset data/raw/sample
```

You should see a progress bar and a summary at the end.

### 8. Start the API

```bash
uvicorn src.api.main:app --reload
```

Leave this running. Open another terminal for the next step.

### 9. Start the demo

```bash
streamlit run frontend/streamlit_app/app.py
```

Visit http://localhost:8501 in your browser. Try a text query like "dog" or upload one of the sample images.

## What to Try Next

Once everything is working, here are good first contributions to make this project your own:

1. **Run the exploration notebooks.** Open `notebooks/01_explore_siglip.py` in VS Code (with the Python and Jupyter extensions installed) and run cells one by one. This is the fastest way to understand what the model is doing under the hood.
2. **Index a bigger dataset.** Download 1000+ images from Unsplash and re-run the indexing.
3. **Add a new endpoint.** For example, an endpoint that returns the most popular queries.
4. **Improve the UI.** Add filters, image categories, or a "more like this" button on each result.
5. **Benchmark.** Run `notebooks/03_benchmark_latency.py` to measure search latency on your hardware. The script saves results to `docs/benchmarks/`.
6. **Add the Redis cache.** The `src/services/` layer leaves room for a cache wrapper that the API can use to skip embedding for repeated queries.

## When Things Go Wrong

### "Cannot connect to Docker daemon"
Make sure Docker Desktop is running. On Linux, you may need to add yourself to the `docker` group.

### "OSError: [Errno 28] No space left on device"
Clear the model cache: `rm -rf ~/.cache/huggingface`. The model will be re-downloaded next time.

### Indexing is very slow
This is normal on CPU. SigLIP processing is roughly 100ms per image on a typical laptop. For 10,000 images, expect 15-20 minutes. On GPU, it is closer to 5 minutes.

### "Connection refused" when calling the API
Make sure both `uvicorn` and `docker compose up qdrant` are running.

## Where to Go from Here

- Read [docs/ARCHITECTURE.md](ARCHITECTURE.md) to understand how the pieces fit together.
- Read [docs/DEVELOPMENT.md](DEVELOPMENT.md) for testing, linting, and contribution workflow.
- Read the SigLIP paper if you are curious about the embedding model: https://arxiv.org/abs/2303.15343
