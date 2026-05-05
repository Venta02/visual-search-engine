# %% [markdown]
# # Exploring SigLIP
#
# SigLIP is a vision-language model that projects images and text into a
# shared embedding space. This notebook walks through its basic behavior
# so we have a feel for what it produces before building on top of it.

# %%
import sys
from pathlib import Path

# Add project root to path so `src` imports work
project_root = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(project_root))

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from src.services.embedding import SigLIPEmbedder

# %% [markdown]
# ## 1. Load the model
#
# The first time this runs it downloads the model weights (~800 MB) from
# Hugging Face. Subsequent runs use the local cache.

# %%
embedder = SigLIPEmbedder()

print(f"Model:         {embedder.model_name}")
print(f"Device:        {embedder.device}")
print(f"Embedding dim: {embedder.embedding_dim}")
print(f"Batch size:    {embedder.batch_size}")

# %% [markdown]
# ## 2. Embed a text query
#
# The processor tokenizes the text, then the model produces a 768-dim
# vector. We L2-normalize it inside the embedder so cosine similarity
# reduces to a dot product.

# %%
text_query = "a photo of a golden retriever"
text_emb = embedder.embed_text(text_query)

print(f"Shape: {text_emb.shape}")
print(f"Dtype: {text_emb.dtype}")
print(f"Norm:  {np.linalg.norm(text_emb):.6f}")  # should be ~1.0
print(f"Min:   {text_emb.min():.4f}")
print(f"Max:   {text_emb.max():.4f}")
print(f"Mean:  {text_emb.mean():.4f}")

# %% [markdown]
# ## 3. Embed an image
#
# Replace the path below with any local image file. The model accepts
# PIL Images or paths.

# %%
# Use a sample image if you ran scripts/download_sample_dataset.py
sample_path = Path("data/raw/sample/sample_000.jpg")

if sample_path.exists():
    image = Image.open(sample_path).convert("RGB")
    image_emb = embedder.embed_image(image)

    print(f"Shape: {image_emb.shape}")
    print(f"Norm:  {np.linalg.norm(image_emb):.6f}")

    # Show the image alongside its embedding fingerprint
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].imshow(image)
    axes[0].set_title("Input image")
    axes[0].axis("off")

    axes[1].plot(image_emb)
    axes[1].set_title("Embedding values across 768 dimensions")
    axes[1].set_xlabel("Dimension")
    axes[1].set_ylabel("Value")
    plt.tight_layout()
    plt.show()
else:
    print(f"Sample image not found at {sample_path}")
    print("Run: python scripts/download_sample_dataset.py")

# %% [markdown]
# ## 4. Cross-modal similarity
#
# The whole point of SigLIP is that text and image embeddings live in the
# same space, so we can compute similarity between modalities. A good
# alignment means the description matches the image.

# %%
if sample_path.exists():
    candidates = [
        "a photograph of a cat",
        "a dog playing in a park",
        "a mountain landscape",
        "a city street at night",
        "a bowl of fruit",
    ]
    similarities = []
    for text in candidates:
        emb = embedder.embed_text(text)
        sim = float(image_emb @ emb)
        similarities.append((text, sim))

    # Sort by similarity, highest first
    similarities.sort(key=lambda x: x[1], reverse=True)

    print(f"Image: {sample_path.name}\n")
    print("Ranked text similarities:")
    for text, sim in similarities:
        bar = "█" * int(sim * 50) if sim > 0 else ""
        print(f"  {sim:+.4f}  {bar} {text}")

# %% [markdown]
# ## 5. Distribution of embedding values
#
# A healthy embedding has values spread across many dimensions, not
# concentrated in a few. Plotting the histogram gives a quick sanity
# check that the model is producing useful representations.

# %%
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].hist(text_emb, bins=50, color="steelblue", alpha=0.7)
axes[0].set_title(f'Text embedding: "{text_query}"')
axes[0].set_xlabel("Value")
axes[0].set_ylabel("Count")
axes[0].axvline(0, color="red", linestyle="--", linewidth=0.5)

if sample_path.exists():
    axes[1].hist(image_emb, bins=50, color="darkorange", alpha=0.7)
    axes[1].set_title("Image embedding")
    axes[1].set_xlabel("Value")
    axes[1].axvline(0, color="red", linestyle="--", linewidth=0.5)

plt.tight_layout()
plt.show()

# %% [markdown]
# ## What to try next
#
# - Embed several different texts and visualize them in 2D using UMAP.
#   See `02_visualize_embeddings.py`.
# - Measure how long embedding takes for different batch sizes. See
#   `03_benchmark_latency.py`.
# - Compare SigLIP base against SigLIP large by changing the model name
#   in the embedder constructor: `SigLIPEmbedder(model_name="google/siglip-large-patch16-384")`.
