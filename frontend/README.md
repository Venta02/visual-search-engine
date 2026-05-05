# Frontend

Two frontend implementations live here:

- `streamlit_app/` is the MVP demo for fast iteration. Use this during development.
- `nextjs_app/` (planned, Phase 4) will be the production-grade UI.

## Running the Streamlit Demo

Make sure the API is running on `http://localhost:8000`, then:

```bash
streamlit run frontend/streamlit_app/app.py
```

Visit http://localhost:8501 in your browser.

## Configuration

The API URL can be changed in the sidebar. By default it points to `http://localhost:8000`.
