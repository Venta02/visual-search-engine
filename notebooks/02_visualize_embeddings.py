# %% [markdown]
# # Visualizing the SigLIP Embedding Space
#
# Embeddings live in a high-dimensional space (768 dimensions for SigLIP base).
# We cannot see 768 dimensions directly, but we can use dimensionality
# reduction algorithms like UMAP or t-SNE to project them into 2D.
#
# A good embedding model produces a space where similar things cluster
# together. We will verify this with both text and image embeddings.

# %%
import sys
from pathlib import Path

project_root = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(project_root))

import numpy as np
import matplotlib.pyplot as plt

from src.services.embedding import SigLIPEmbedder

# %% [markdown]
# ## 1. Define a small set of concepts grouped by category
#
# Each group should be semantically coherent. If the model is doing its
# job, items in the same group will land near each other in the projection.

# %%
concept_groups = {
    "animals": [
        "a photograph of a cat",
        "a photograph of a dog",
        "a photograph of a horse",
        "a photograph of a rabbit",
        "a photograph of a bird",
        "a photograph of a fish",
    ],
    "vehicles": [
        "a photograph of a car",
        "a photograph of a truck",
        "a photograph of a motorcycle",
        "a photograph of a bicycle",
        "a photograph of a bus",
        "a photograph of a train",
    ],
    "food": [
        "a photograph of pizza",
        "a photograph of a burger",
        "a photograph of sushi",
        "a photograph of pasta",
        "a photograph of a salad",
        "a photograph of bread",
    ],
    "nature": [
        "a photograph of a mountain",
        "a photograph of a forest",
        "a photograph of a beach",
        "a photograph of a river",
        "a photograph of a desert",
        "a photograph of a waterfall",
    ],
}

# Flatten into parallel lists for embedding
all_texts: list[str] = []
all_labels: list[str] = []
for category, texts in concept_groups.items():
    for text in texts:
        all_texts.append(text)
        all_labels.append(category)

print(f"Total texts: {len(all_texts)}")
print(f"Categories:  {list(concept_groups.keys())}")

# %% [markdown]
# ## 2. Embed all texts
#
# We embed them one at a time here for simplicity. For large-scale
# experiments, use the batch interface.

# %%
embedder = SigLIPEmbedder()

embeddings = np.array(
    [embedder.embed_text(text) for text in all_texts],
    dtype=np.float32,
)

print(f"Embeddings shape: {embeddings.shape}")

# %% [markdown]
# ## 3. Project to 2D with UMAP
#
# UMAP preserves both local structure (nearby points stay nearby) and
# some global structure (clusters maintain relative position). For
# small N like this, t-SNE would also work.

# %%
try:
    import umap

    reducer = umap.UMAP(
        n_neighbors=5,
        min_dist=0.3,
        metric="cosine",
        random_state=42,
    )
    coords = reducer.fit_transform(embeddings)

    print(f"Reduced shape: {coords.shape}")
except ImportError:
    print("UMAP not installed. Falling back to PCA.")
    print("Install with: pip install umap-learn")
    from sklearn.decomposition import PCA

    coords = PCA(n_components=2, random_state=42).fit_transform(embeddings)

# %% [markdown]
# ## 4. Plot
#
# Color points by their category. Well-separated clusters mean the model
# distinguishes the concepts cleanly.

# %%
fig, ax = plt.subplots(figsize=(10, 8))

color_map = {
    "animals": "tab:blue",
    "vehicles": "tab:orange",
    "food": "tab:green",
    "nature": "tab:red",
}

for category in concept_groups:
    mask = np.array([label == category for label in all_labels])
    ax.scatter(
        coords[mask, 0],
        coords[mask, 1],
        c=color_map[category],
        label=category,
        s=120,
        alpha=0.7,
        edgecolors="white",
        linewidths=1.5,
    )

# Annotate each point with the last word of its text
for i, text in enumerate(all_texts):
    label = text.split()[-1]
    ax.annotate(
        label,
        coords[i],
        fontsize=8,
        xytext=(5, 5),
        textcoords="offset points",
        alpha=0.7,
    )

ax.set_title("SigLIP text embeddings projected to 2D", fontsize=14)
ax.set_xlabel("Component 1")
ax.set_ylabel("Component 2")
ax.legend(loc="best", framealpha=0.9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# %% [markdown]
# ## 5. Quantitative check: average intra-cluster vs inter-cluster similarity
#
# A useful sanity metric: items in the same group should have higher
# average similarity to each other than to items in other groups.

# %%
similarity_matrix = embeddings @ embeddings.T

intra_sims: list[float] = []
inter_sims: list[float] = []

for i in range(len(all_texts)):
    for j in range(i + 1, len(all_texts)):
        sim = float(similarity_matrix[i, j])
        if all_labels[i] == all_labels[j]:
            intra_sims.append(sim)
        else:
            inter_sims.append(sim)

print(f"Intra-category similarity: {np.mean(intra_sims):.4f} (mean), {np.std(intra_sims):.4f} (std)")
print(f"Inter-category similarity: {np.mean(inter_sims):.4f} (mean), {np.std(inter_sims):.4f} (std)")
print(f"Separation:                {np.mean(intra_sims) - np.mean(inter_sims):.4f}")

# Plot the distributions
fig, ax = plt.subplots(figsize=(10, 4))
ax.hist(intra_sims, bins=20, alpha=0.6, label="Same category", color="green")
ax.hist(inter_sims, bins=20, alpha=0.6, label="Different category", color="red")
ax.set_xlabel("Cosine similarity")
ax.set_ylabel("Count")
ax.set_title("Distribution of pairwise similarities")
ax.legend()
plt.tight_layout()
plt.show()

# %% [markdown]
# ## What to try next
#
# - Add image embeddings to the same plot to verify cross-modal alignment.
# - Try harder concepts (e.g., "happy" vs "sad" expressions) to see how
#   the model handles abstract attributes.
# - Replace UMAP with t-SNE and compare the layouts.
# - Use a larger model variant and see if the separation improves.
