# Installation & Notebook Guide

Comprehensive step-by-step guide from a fresh machine to running all exploration notebooks. Follow this in order — do not skip steps.

> **For:** First-time users on Windows, macOS, or Linux who want to run the project end-to-end including the exploration notebooks.

---

## Table of Contents

1. [Prerequisites Check](#1-prerequisites-check)
2. [Install System Tools](#2-install-system-tools)
3. [Install VS Code Extensions](#3-install-vs-code-extensions)
4. [Project Setup](#4-project-setup)
5. [Install Python Dependencies](#5-install-python-dependencies)
6. [Start Infrastructure Services](#6-start-infrastructure-services)
7. [Configure VS Code for Notebooks](#7-configure-vs-code-for-notebooks)
8. [Running the Notebooks](#8-running-the-notebooks)
9. [Running the Full Application](#9-running-the-full-application)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Prerequisites Check

Before starting, verify your machine meets the minimum requirements:

| Requirement | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Free disk space | 10 GB | 20 GB |
| OS | Windows 10, macOS 11, Ubuntu 20.04 | Latest versions |
| Internet | Required for first-time model download (~800 MB) | Stable connection |

Check your current setup:

**Windows (PowerShell):**
```powershell
# Check RAM
Get-WmiObject Win32_PhysicalMemory | Measure-Object Capacity -Sum

# Check disk space
Get-PSDrive C
```

**macOS / Linux (Terminal):**
```bash
# Check RAM
free -h            # Linux
sysctl hw.memsize  # macOS

# Check disk space
df -h
```

---

## 2. Install System Tools

### 2.1 Python 3.10 or Higher

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. **IMPORTANT:** Check "Add Python to PATH" before clicking Install
4. Verify in PowerShell: `python --version`

**macOS:**
```bash
# Using Homebrew (install Homebrew first if you don't have it)
brew install python@3.11
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
python3 --version
```

### 2.2 Git

**Windows:** Download from https://git-scm.com/download/win

**macOS:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

Verify: `git --version`

### 2.3 Docker Desktop

This runs Qdrant (vector database) and Redis (cache) for you.

**Windows / macOS:**
1. Download from https://www.docker.com/products/docker-desktop/
2. Install and restart computer if prompted
3. Open Docker Desktop and let it finish initial setup
4. Wait until you see "Docker Desktop is running" in the bottom-left

**Linux:**
```bash
# Install Docker Engine + Compose plugin
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and log back in for group change to take effect
```

Verify:
```bash
docker --version
docker compose version
```

You should see version numbers for both.

### 2.4 VS Code

Download from https://code.visualstudio.com/ and install with default settings.

---

## 3. Install VS Code Extensions

Open VS Code, then:

1. Press `Ctrl + Shift + X` (Windows/Linux) or `Cmd + Shift + X` (macOS) to open Extensions panel
2. Search and install each of these:

**Required:**
- **Python** (by Microsoft) — Python language support
- **Jupyter** (by Microsoft) — Enables `# %%` cells for interactive Python
- **Pylance** (by Microsoft) — Type checking and autocomplete

**Recommended:**
- **Docker** (by Microsoft) — Manage Docker containers from VS Code
- **Even Better TOML** — Syntax highlighting for `pyproject.toml`
- **YAML** (by Red Hat) — Syntax highlighting for YAML files
- **GitLens** — Enhanced Git integration

After installing, restart VS Code.

---

## 4. Project Setup

### 4.1 Extract the ZIP

If you received `visual-search-engine.zip`, extract it to a folder you can find easily, for example:
- Windows: `C:\Users\YourName\Projects\visual-search-engine\`
- macOS: `/Users/YourName/Projects/visual-search-engine/`
- Linux: `/home/yourname/projects/visual-search-engine/`

### 4.2 Open in VS Code

1. Open VS Code
2. File → Open Folder
3. Select the extracted `visual-search-engine` folder
4. Click "Yes, I trust the authors" if prompted

### 4.3 Open Integrated Terminal

Press `` Ctrl + ` `` (backtick) or go to Terminal → New Terminal.

You should see a terminal at the bottom of VS Code, already in the project directory. All commands below run here.

---

## 5. Install Python Dependencies

### 5.1 Create a Virtual Environment

A virtual environment isolates this project's dependencies from your system Python.

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get an "execution policy" error on PowerShell:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# Then try activation again
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

After activation, your terminal prompt should show `(venv)` at the start. This means you are inside the virtual environment.

### 5.2 Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 5.3 Install Dependencies

```bash
pip install -r requirements.txt
```

This will take **5-15 minutes** the first time. PyTorch alone is around 2 GB. Be patient.

Common packages being installed:
- `torch` and `transformers` for SigLIP
- `qdrant-client` for vector database
- `fastapi` and `uvicorn` for the API
- `streamlit` for the demo UI
- `matplotlib`, `umap-learn`, `scikit-learn` for notebook visualizations

### 5.4 Verify Installation

```bash
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import transformers; print('Transformers:', transformers.__version__)"
python -c "import qdrant_client; print('Qdrant client OK')"
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"
```

All four lines should print version numbers without errors.

### 5.5 Configure Environment Variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` in VS Code and review the settings. The defaults work for most users. If you have an NVIDIA GPU and want to use it, change:

```
EMBEDDING_DEVICE=cpu
```

to:

```
EMBEDDING_DEVICE=cuda
```

---

## 6. Start Infrastructure Services

### 6.1 Verify Docker is Running

Make sure Docker Desktop is open and shows "Docker Desktop is running" status.

### 6.2 Start Qdrant and Redis

In the VS Code terminal:

```bash
docker compose up -d qdrant redis
```

The `-d` flag runs them in the background. First time will pull Docker images (around 200 MB).

### 6.3 Verify Services

```bash
docker compose ps
```

You should see two containers `vse-qdrant` and `vse-redis` with status `running` (and `healthy` once health checks pass after about 30 seconds).

Test Qdrant directly:

```bash
# Windows PowerShell
Invoke-WebRequest http://localhost:6333/healthz

# macOS / Linux
curl http://localhost:6333/healthz
```

You should see "healthz check passed" or similar.

### 6.4 (Optional) Start Monitoring Stack

If you want to play with Prometheus and Grafana later:

```bash
docker compose up -d prometheus grafana
```

Access:
- Grafana: http://localhost:3000 (login: `admin` / `admin`)
- Prometheus: http://localhost:9090

---

## 7. Configure VS Code for Notebooks

### 7.1 Select the Python Interpreter

This is critical — VS Code needs to know which Python to use.

1. Press `Ctrl + Shift + P` (Windows/Linux) or `Cmd + Shift + P` (macOS)
2. Type "Python: Select Interpreter"
3. Choose the one inside your `venv` folder. It should look like:
   - Windows: `.\venv\Scripts\python.exe`
   - macOS / Linux: `./venv/bin/python`

You should see "Python 3.11.x ('venv')" or similar in the bottom-right status bar.

### 7.2 Verify Jupyter Extension Detects venv

1. Open `notebooks/01_explore_siglip.py`
2. Look at the top of the file for "Run Cell" buttons that should appear above each `# %%` marker

If you do not see "Run Cell" buttons, restart VS Code and reload the window:
- `Ctrl + Shift + P` → "Developer: Reload Window"

---

## 8. Running the Notebooks

### 8.1 Notebook Workflow

The notebooks use the `# %%` cell format. Each cell is a section of code that runs independently.

To run a cell:
- Click "Run Cell" link above the `# %%` marker, OR
- Place cursor inside the cell and press `Shift + Enter`, OR
- Use Run All (the play button at the top of the file) to run everything

The first time you run a cell, an "Interactive Window" opens on the side. Subsequent cells run in the same kernel, so variables persist between cells.

### 8.2 Notebook 01: Explore SigLIP

**File:** `notebooks/01_explore_siglip.py`

**Goal:** Understand what SigLIP does. This is your starting point.

**Steps:**

1. Open the file in VS Code
2. Run cells one by one in order, top to bottom

**What happens cell by cell:**

| Cell | What it does | Expected output | Time |
|---|---|---|---|
| 1 (imports) | Loads numpy, matplotlib, embedder | Nothing printed | 2-5 sec |
| 2 (load model) | Downloads SigLIP from Hugging Face (first time) | Model info printed | 30 sec - 5 min first time, 10 sec after |
| 3 (embed text) | Embeds "a photo of a golden retriever" | Shape, dtype, norm printed | 1-2 sec |
| 4 (embed image) | Embeds a sample image, plots it side by side with embedding | Image and line plot displayed | 1-2 sec |
| 5 (cross-modal) | Compares image to 5 different text candidates | Ranked similarity scores | 2-3 sec |
| 6 (histogram) | Plots distribution of embedding values | Two histograms displayed | < 1 sec |

**Common issues:**
- "FileNotFoundError: data/raw/sample/sample_000.jpg" → run `python scripts/download_sample_dataset.py` first
- Model download is slow → check your internet connection; the first download is ~800 MB

### 8.3 Notebook 02: Visualize Embeddings

**File:** `notebooks/02_visualize_embeddings.py`

**Goal:** See how SigLIP separates different concepts in 2D.

**Prerequisite:** Run Notebook 01 first to confirm the model loads correctly.

**Steps:**

1. Open the file
2. Run cells in order
3. The UMAP cell takes 5-10 seconds the first time
4. The plot cell shows a 2D scatter plot with 4 colored clusters

**What you should see:**
- Animals (blue), vehicles (orange), food (green), nature (red) form four distinct clusters
- Items within the same cluster are close to each other
- The intra-category similarity should be higher than inter-category

**If clusters look mixed:**
- This is normal for some random seed values
- Try changing `random_state=42` to another number
- Check that the embeddings array has the correct shape (24, 768)

### 8.4 Notebook 03: Benchmark Latency

**File:** `notebooks/03_benchmark_latency.py`

**Goal:** Measure how fast embeddings are on your machine.

**Prerequisite:** Notebook 01 should already be working.

**Steps:**

1. Open the file
2. Run cells in order
3. The batch throughput cell takes about 1-2 minutes (it runs many embeddings)

**What you get:**
- Hardware info printed for context
- Mean, stdev, min, max latency for text embeddings
- Same statistics for image embeddings
- Two plots: latency per image and throughput by batch size
- A CSV file saved to `docs/benchmarks/embedding_latency.csv`

**Expected numbers (rough order of magnitude):**

| Hardware | Single text | Single image | Batch 32 |
|---|---|---|---|
| CPU only (modern laptop) | 30-100 ms | 50-200 ms | 200-800 ms |
| GPU (RTX 3050 / 3060) | 10-30 ms | 20-50 ms | 50-150 ms |
| GPU (RTX 4090 / A100) | 5-15 ms | 5-20 ms | 20-60 ms |

If your numbers are far worse, see Troubleshooting below.

### 8.5 Saving Notebook Outputs

VS Code Interactive Window outputs are not saved automatically. To save them:

1. Right-click any output → "Export As" → choose Jupyter Notebook
2. Or click the "Save" icon at the top of the Interactive Window
3. Or use "Export to Python script" if you want a clean `.py` file

For portfolio purposes, save key plots as PNG:
```python
plt.savefig("docs/benchmarks/latency_plot.png", dpi=150, bbox_inches="tight")
```

---

## 9. Running the Full Application

After exploring with notebooks, you can run the actual application.

### 9.1 Download Sample Dataset

```bash
python scripts/download_sample_dataset.py
```

This downloads 10 sample images to `data/raw/sample/`. Takes about 30 seconds.

### 9.2 Build the Index

```bash
python scripts/build_index.py --dataset data/raw/sample
```

This:
1. Loads SigLIP model (uses cache after first time)
2. Reads each image
3. Extracts embeddings in batches
4. Inserts into Qdrant

You should see a progress bar and a summary at the end.

### 9.3 Start the API

In one terminal:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Leave this running. You should see startup logs ending with "Application ready".

Test the API: http://localhost:8000/docs

### 9.4 Start the Streamlit Demo

Open a **second** terminal in VS Code (click the `+` icon in the terminal panel).

Activate the venv again in this new terminal:

```bash
# Windows
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

Then:

```bash
streamlit run frontend/streamlit_app/app.py
```

Browser opens automatically at http://localhost:8501.

### 9.5 Try the Demo

In the Streamlit UI:

1. **Search by text:** Type "dog" or "mountain" and click Search
2. **Search by image:** Upload one of the images from `data/raw/sample/`
3. **Health check:** Click "Check API health" in the sidebar — should show indexed count

---

## 10. Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"

**Cause:** Python cannot find the project source.

**Fix:** Make sure you are in the project root directory and the venv is activated. Run from project root, not from inside `notebooks/`:

```bash
# Check current directory
pwd  # macOS/Linux
cd   # Windows (just shows path)

# Should show: .../visual-search-engine
```

If running a notebook gives this error, check that the first cell adds the project root to `sys.path` (it should — it is in the template).

### Issue: "Cannot connect to Qdrant"

**Cause:** Docker is not running or Qdrant container stopped.

**Fix:**

```bash
docker compose ps
```

If Qdrant is not running:

```bash
docker compose up -d qdrant redis
```

If Docker Desktop is not running, open it first.

### Issue: Out of memory during embedding

**Cause:** Default batch size is too large for 8 GB RAM.

**Fix:** Edit `.env` file:

```
EMBEDDING_BATCH_SIZE=8
```

Restart whatever you are running.

### Issue: "Microsoft Visual C++ 14.0 is required" (Windows only)

**Cause:** Some Python packages need a C++ compiler.

**Fix:** Download "Build Tools for Visual Studio" from Microsoft. During install, check "Desktop development with C++".

### Issue: SigLIP download fails or hangs

**Cause:** Slow internet or Hugging Face server issues.

**Fix:**
1. Check if you can access https://huggingface.co in browser
2. Set Hugging Face to use a mirror in `.env`:
   ```
   HF_ENDPOINT=https://hf-mirror.com
   ```
3. Or download manually then point to local cache

### Issue: Plots do not show in Interactive Window

**Cause:** Matplotlib backend not configured.

**Fix:** Add this at the top of the notebook:

```python
import matplotlib
matplotlib.use("module://matplotlib_inline.backend_inline")
```

Then restart the Python kernel: `Ctrl + Shift + P` → "Jupyter: Restart Kernel".

### Issue: "Run Cell" buttons not appearing

**Cause:** Jupyter extension not active or wrong interpreter.

**Fix:**
1. Verify Python and Jupyter extensions are installed and enabled
2. Select the venv interpreter (Step 7.1)
3. Reload the window: `Ctrl + Shift + P` → "Developer: Reload Window"

### Issue: UMAP installation fails

**Cause:** UMAP has complex C dependencies on some systems.

**Fix:** Install via conda or use the PCA fallback:

```bash
# Option 1: skip UMAP, the notebook falls back to PCA automatically
pip install scikit-learn

# Option 2: install via conda if you use it
conda install -c conda-forge umap-learn
```

### Issue: Streamlit page is blank or shows errors

**Cause:** API not running or wrong port.

**Fix:**
1. Confirm API is running: visit http://localhost:8000/docs
2. In the Streamlit sidebar, check "API URL" matches the running API
3. Click "Check API health" — should show success

### Issue: Slow first request to API

**Cause:** Model has not been loaded yet (cold start).

**Fix:** This is expected. The first request takes 10-30 seconds because the model loads. Subsequent requests are fast. To pre-warm, use the worker task:

```bash
celery -A src.workers.celery_app worker --loglevel=info
```

Then in another terminal, trigger the warm-up task.

---

## Quick Reference Card

Bookmark this section for daily use after the initial setup.

### Daily Startup

```bash
# 1. Open VS Code in project folder
# 2. Activate venv
source venv/bin/activate         # macOS/Linux
.\venv\Scripts\Activate.ps1      # Windows

# 3. Start services
docker compose up -d qdrant redis

# 4. Run whatever you need
uvicorn src.api.main:app --reload                 # API
streamlit run frontend/streamlit_app/app.py       # Demo UI
python scripts/build_index.py --dataset ...       # Reindex
```

### Daily Shutdown

```bash
# Stop API/Streamlit: Ctrl+C in their terminals
# Stop Docker services
docker compose down

# Deactivate venv (optional)
deactivate
```

### Useful Commands

```bash
# Run tests
pytest tests/unit -v

# Check linting
ruff check src/

# Format code
black src/

# Use Makefile shortcuts
make help                # show all available commands
make dev                 # start API
make demo                # start Streamlit
make test                # run tests
make docker-up           # start services
make docker-down         # stop services
```

### Next Steps

After you have everything running:

1. **Read** `docs/ARCHITECTURE.md` to understand the design
2. **Read** `docs/adr/0001-use-siglip-as-default-embedding.md` as an example of decision documentation
3. **Modify** the code — start with the Streamlit UI, the safest place to experiment
4. **Build** something new in `src/` and write tests for it
5. **Document** your changes in a new ADR under `docs/adr/`

Happy building.
