# VIRA Iteration 1 Prototype

Prototype implementation of the Venture Intelligence Research Assistant (Iteration 1), focused on ingesting curated a16z content, running a hybrid RAG pipeline, and delivering structured alignment analyses for uploaded business plans.

## Project Structure

- `config/` – Environment and settings templates.
- `data/raw/` – Raw crawled HTML/text snapshots.
- `data/processed/` – Cleaned JSONL chunks and vector store artifacts.
- `src/vira/` – Python package with ingestion, processing, retrieval, backend, and UI modules.
- `notebooks/` – Evaluation and exploratory notebooks.
- `tests/` – Automated test suites.

## Getting Started

1. **Install dependencies**
   ```bash
   uv pip install -r <(uv pip compile pyproject.toml)
   ```
   Or use the tooling of your choice (`pip`, `poetry`). Python 3.10+ is required.

2. **Environment variables**
   - Copy `config/.env.template` to `.env` at the project root.
   - Populate `OPENAI_API_KEY`, `LANGCHAIN_API_KEY` (optional for LangSmith), and any crawl configuration overrides.

3. **Run the crawler**
   ```bash
   vira-crawl --config config/crawl_settings.yaml
   ```
   Outputs land in `data/raw/`.

4. **Process & embed content**
   ```bash
   vira-process --raw-path data/raw/a16z_raw.jsonl
   ```

5. **Launch the API**
   ```bash
   uvicorn vira.backend.api:app --reload
   ```

6. **Start the Streamlit UI**
   ```bash
   streamlit run src/vira/ui/app.py
   ```

## Tooling

- Linting: `ruff check src tests`
- Formatting: `black src tests`
- Type checking: `mypy src`
- Tests: `pytest`

See inline module docstrings for implementation details and integration notes for Iteration 2 planning.

