# %% [markdown]
# # Latency Benchmark
#
# Two questions to answer:
#
# 1. What is the latency of a single embedding call (cold and warm)?
# 2. How does batching affect throughput?
#
# Answers depend heavily on hardware, so always note the device, RAM,
# and CPU/GPU model in any benchmark report.

# %%
import sys
import time
import platform
from pathlib import Path
from statistics import mean, stdev

project_root = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(project_root))

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from src.services.embedding import SigLIPEmbedder

# %% [markdown]
# ## 0. Hardware context
#
# Always report the hardware. A benchmark without context is meaningless.

# %%
import torch

print("=== Hardware ===")
print(f"OS:       {platform.system()} {platform.release()}")
print(f"Python:   {platform.python_version()}")
print(f"PyTorch:  {torch.__version__}")
print(f"CUDA:     {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU:      {torch.cuda.get_device_name(0)}")
print(f"CPU:      {platform.processor() or 'unknown'}")

# %% [markdown]
# ## 1. Load the model
#
# The first call after load is slower than subsequent calls because
# weights are still being moved to the right device and JIT compiled.

# %%
embedder = SigLIPEmbedder()

# %% [markdown]
# ## 2. Single text embedding latency
#
# We run the same query multiple times. The first run is the cold-start.

# %%
def benchmark_text(query: str, n_runs: int = 20, warmup: int = 3):
    """Time text embedding, discarding warmup runs."""
    timings = []

    for i in range(warmup + n_runs):
        start = time.perf_counter()
        embedder.embed_text(query)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        if i >= warmup:
            timings.append(elapsed)

    return timings


text_timings = benchmark_text("a photo of a cat sitting on a windowsill")

print(f"Runs:   {len(text_timings)}")
print(f"Mean:   {mean(text_timings):.2f} ms")
print(f"Stdev:  {stdev(text_timings):.2f} ms")
print(f"Min:    {min(text_timings):.2f} ms")
print(f"Max:    {max(text_timings):.2f} ms")
print(f"Median: {sorted(text_timings)[len(text_timings) // 2]:.2f} ms")

# %% [markdown]
# ## 3. Single image embedding latency
#
# Image processing involves resizing, normalization, and a forward pass
# through the vision tower. Generally slower than text embedding because
# the input is a 224x224x3 tensor versus a short token sequence.

# %%
def make_dummy_image(size: int = 224) -> Image.Image:
    """Create a random RGB image for benchmarking."""
    arr = np.random.randint(0, 255, size=(size, size, 3), dtype=np.uint8)
    return Image.fromarray(arr)


def benchmark_image(image: Image.Image, n_runs: int = 20, warmup: int = 3):
    timings = []
    for i in range(warmup + n_runs):
        start = time.perf_counter()
        embedder.embed_image(image)
        elapsed = (time.perf_counter() - start) * 1000
        if i >= warmup:
            timings.append(elapsed)
    return timings


image_timings = benchmark_image(make_dummy_image())

print(f"Runs:   {len(image_timings)}")
print(f"Mean:   {mean(image_timings):.2f} ms")
print(f"Stdev:  {stdev(image_timings):.2f} ms")
print(f"Median: {sorted(image_timings)[len(image_timings) // 2]:.2f} ms")

# %% [markdown]
# ## 4. Batch throughput
#
# Larger batches amortize fixed overhead (Python overhead, kernel
# launches) over more items. We expect throughput to rise with batch
# size up to a saturation point.

# %%
batch_sizes = [1, 2, 4, 8, 16, 32]
throughput_results = []

for bs in batch_sizes:
    images = [make_dummy_image() for _ in range(bs)]

    # Warmup
    embedder.embed_images_batch(images)

    # Time three runs
    runs = []
    for _ in range(3):
        start = time.perf_counter()
        embedder.embed_images_batch(images)
        runs.append(time.perf_counter() - start)

    avg_seconds = mean(runs)
    images_per_second = bs / avg_seconds
    ms_per_image = (avg_seconds / bs) * 1000

    throughput_results.append(
        {
            "batch_size": bs,
            "total_ms": avg_seconds * 1000,
            "ms_per_image": ms_per_image,
            "images_per_second": images_per_second,
        }
    )

    print(
        f"BS={bs:>3}: {avg_seconds * 1000:>7.1f} ms total, "
        f"{ms_per_image:>5.1f} ms/img, "
        f"{images_per_second:>5.1f} img/s"
    )

# %% [markdown]
# ## 5. Plot results

# %%
sizes = [r["batch_size"] for r in throughput_results]
ms_per_image = [r["ms_per_image"] for r in throughput_results]
throughput = [r["images_per_second"] for r in throughput_results]

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].plot(sizes, ms_per_image, marker="o", linewidth=2)
axes[0].set_xlabel("Batch size")
axes[0].set_ylabel("ms per image")
axes[0].set_title("Latency per image vs batch size")
axes[0].set_xscale("log", base=2)
axes[0].grid(True, alpha=0.3)

axes[1].plot(sizes, throughput, marker="s", color="darkorange", linewidth=2)
axes[1].set_xlabel("Batch size")
axes[1].set_ylabel("Images per second")
axes[1].set_title("Throughput vs batch size")
axes[1].set_xscale("log", base=2)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# %% [markdown]
# ## 6. Latency distribution
#
# Distribution shape matters for SLAs. A long tail means some users see
# bad latency even when the mean looks good.

# %%
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].hist(text_timings, bins=15, color="steelblue", alpha=0.7, edgecolor="black")
axes[0].axvline(mean(text_timings), color="red", linestyle="--", label=f"Mean = {mean(text_timings):.1f} ms")
axes[0].set_xlabel("Latency (ms)")
axes[0].set_ylabel("Count")
axes[0].set_title("Text embedding latency distribution")
axes[0].legend()

axes[1].hist(image_timings, bins=15, color="darkorange", alpha=0.7, edgecolor="black")
axes[1].axvline(mean(image_timings), color="red", linestyle="--", label=f"Mean = {mean(image_timings):.1f} ms")
axes[1].set_xlabel("Latency (ms)")
axes[1].set_ylabel("Count")
axes[1].set_title("Image embedding latency distribution")
axes[1].legend()

plt.tight_layout()
plt.show()

# %% [markdown]
# ## 7. Save results to CSV
#
# So you can include the table in a benchmark report later.

# %%
import csv

results_path = project_root / "docs" / "benchmarks" / "embedding_latency.csv"
results_path.parent.mkdir(parents=True, exist_ok=True)

with open(results_path, "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["batch_size", "total_ms", "ms_per_image", "images_per_second"],
    )
    writer.writeheader()
    writer.writerows(throughput_results)

print(f"Saved results to {results_path}")

# %% [markdown]
# ## Conclusions to write up
#
# After running this on your actual hardware, write up the findings:
#
# - What is the cold-start latency for the first request?
# - What is the steady-state mean and p95 for single-item embedding?
# - At what batch size does throughput saturate? Why?
# - How does CPU compare to GPU (run this twice if you have a GPU)?
# - What does the latency distribution shape tell you about variance?
#
# These are the kinds of analysis questions that signal real engineering
# maturity in interviews.
