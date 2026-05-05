"""Streamlit demo for the Visual Search Engine.

Run with:
    streamlit run frontend/streamlit_app/app.py
"""
from pathlib import Path

import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Visual Search Engine",
    page_icon="🔍",
    layout="wide",
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def resolve_image_path(filepath: str) -> Path | None:
    """Try several strategies to find the image file on disk."""
    candidates = [
        Path(filepath),                  # as stored
        PROJECT_ROOT / filepath,         # relative to project root
        Path(filepath).resolve(),        # absolute resolution
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def render_results(results: list) -> None:
    """Render search hits as a grid of cards."""
    if not results:
        st.info("No matches found.")
        return

    cols_per_row = 5
    for row_start in range(0, len(results), cols_per_row):
        row = results[row_start : row_start + cols_per_row]
        columns = st.columns(cols_per_row)
        for col, hit in zip(columns, row):
            with col:
                filepath = hit["payload"].get("filepath")
                if filepath:
                    abs_path = resolve_image_path(filepath)
                    if abs_path:
                        st.image(str(abs_path), use_column_width=True)
                    else:
                        st.caption(f"Not found: {filepath}")
                st.caption(f"Score: {hit['score']:.3f}")
                st.caption(hit["payload"].get("filename", str(hit["id"])))

st.title("Visual Search Engine")
st.caption("Multi-modal retrieval powered by SigLIP and Qdrant")


# Sidebar controls
with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("API URL", value=API_URL)
    limit = st.slider("Number of results", min_value=1, max_value=50, value=10)
    score_threshold = st.slider(
        "Minimum score",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05,
    )

    st.divider()
    if st.button("Check API health"):
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            data = response.json()
            if data["status"] == "ok":
                st.success(f"Healthy. Indexed: {data['indexed_count']:,}")
            else:
                st.warning(f"Status: {data['status']}")
        except requests.exceptions.RequestException as e:
            st.error(f"API unreachable: {e}")


# Main tabs
tab_text, tab_image = st.tabs(["Search by text", "Search by image"])

with tab_text:
    st.subheader("Find images by description")
    query = st.text_input(
        "Describe what you are looking for",
        placeholder="a cat sitting on a windowsill at sunset",
    )

    if st.button("Search", key="text_search", type="primary") and query:
        with st.spinner("Searching..."):
            try:
                response = requests.post(
                    f"{api_url}/search/text",
                    json={
                        "query": query,
                        "limit": limit,
                        "score_threshold": score_threshold or None,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                st.error(f"Search failed: {e}")
            else:
                st.success(
                    f"Found {data['total_results']} results in {data['latency_ms']}ms"
                )
                render_results(data["results"])

with tab_image:
    st.subheader("Find similar images")
    uploaded_file = st.file_uploader(
        "Upload a query image",
        type=["png", "jpg", "jpeg", "webp"],
    )

    if uploaded_file is not None:
        col_query, col_action = st.columns([1, 2])
        with col_query:
            st.image(uploaded_file, caption="Query image", use_column_width=True)
        with col_action:
            if st.button("Find similar", key="image_search", type="primary"):
                with st.spinner("Searching..."):
                    try:
                        files = {
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type,
                            )
                        }
                        response = requests.post(
                            f"{api_url}/search/image",
                            files=files,
                            params={"limit": limit},
                            timeout=30,
                        )
                        response.raise_for_status()
                        data = response.json()
                    except requests.exceptions.RequestException as e:
                        st.error(f"Search failed: {e}")
                    else:
                        st.success(
                            f"Found {data['total_results']} results in {data['latency_ms']}ms"
                        )
                        render_results(data["results"])
