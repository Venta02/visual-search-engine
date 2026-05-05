# ADR 0001: Use SigLIP as the Default Embedding Model

**Status:** Accepted
**Date:** 2026-01-15

## Context

The visual search system needs to embed both images and short text queries into a shared vector space so that cross-modal retrieval works. Several pre-trained models are candidates:

- OpenAI CLIP (ViT-B/32 and ViT-L/14 variants)
- Google SigLIP (siglip-base-patch16-224)
- Meta DINOv2 (image-only, no text encoder)
- BLIP-2 (heavy, generative)

Constraints:
- Inference must run on commodity hardware (CPU acceptable, modest GPU preferred).
- Must support both image and text encoders out of the box.
- License must allow commercial use.
- Smaller is preferable so cold-start times stay low.

## Decision

Use **SigLIP base** (`google/siglip-base-patch16-224`) as the default embedding model.

## Rationale

- SigLIP uses a sigmoid loss instead of softmax over the batch, which empirically produces tighter alignments between text and image at smaller scales.
- The base variant has a 768-dimensional output, comparable in size to CLIP ViT-B but with better retrieval benchmarks in published evaluations.
- The model loads in under 10 seconds on CPU and runs at acceptable latency without a GPU.
- Apache 2.0 license, suitable for commercial use.

DINOv2 was rejected because it has no text encoder. Adding a separate text-to-image alignment layer would add complexity. BLIP-2 was rejected for being too heavy for inference on commodity hardware.

## Consequences

### Positive
- Single model handles both modalities consistently.
- Embeddings are compatible across image and text without extra projection layers.
- Easy to swap the model variant later (base, large, so400m) by changing one config value.

### Negative
- 768-dim vectors take more memory than smaller alternatives. At 100k images, that is roughly 300 MB in FP32 (or 75 MB in INT8 after quantization).
- The model is bound to the Hugging Face transformers library, which is heavy. We may revisit and switch to a leaner runtime (ONNX Runtime, TensorRT) in Phase 3.

## Follow-ups
- Benchmark FP16 and INT8 quantized variants in Phase 3.
- Evaluate `siglip-large-patch16-384` for higher recall at the cost of latency.
- Compare against `siglip2` if Google releases an updated checkpoint.
