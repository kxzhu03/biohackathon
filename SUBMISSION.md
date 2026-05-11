# Submission Checklist

Biohackathon 2026 submission package for **PCOS Pathfinder**.

## Include in the submission

- `README.md` - quickstart and results snapshot.
- `PROJECT_PLAN.md` - full design rationale.
- `requirements.txt` - pinned dependencies for reproducibility.
- `notebooks/` - the six numbered analysis notebooks plus `notebooks/README.md`.
- `outputs/`
  - `figures/` - all plots referenced in the deck.
  - `metrics/` - CSV/JSON metric exports, model card, SHAP outputs, single-cell gene overlap.
  - `models/` - joblib model artifacts (screening, enhanced, endometriosis overlap).
  - `pcos_cleaned.csv` - processed PCOS table emitted by notebook 01.
- `scripts/create_training_notebooks.mjs` - deterministic notebook regenerator.
- `src/app.py` - Streamlit prototype.
- The final slide deck (PPTX or PDF) and any speaker notes.

## Exclude from the submission

- `_read_extract/` and `OneDrive_*.zip` - source datasets provided by the organisers; do **not** redistribute unless they explicitly ask for them.
- Large single-cell archives (`*.tar`, `*.tar.gz`) inside `_read_extract/single_cell_peek/`.
- Local virtual environments (`.venv/`, `venv/`).
- Editor / OS junk (`.vscode/`, `.idea/`, `.DS_Store`).
- Notebook checkpoints (`.ipynb_checkpoints/`).

The provided `.gitignore` covers all of the above.

## Pre-submission sanity checks

1. `pip install -r requirements.txt` succeeds on a fresh environment.
2. `node scripts/create_training_notebooks.mjs` regenerates the notebooks without errors.
3. All six notebooks execute end-to-end:
   ```bash
   for nb in notebooks/*.ipynb; do
     python -m nbconvert --to notebook --execute --inplace "$nb"
   done
   ```
4. `streamlit run src/app.py` launches and renders the patient assessment tab.
5. Model artifacts under `outputs/models/` are present and load via `joblib.load`.
6. Held-out metrics in `outputs/metrics/{screening,enhanced,endometriosis}_holdout_metrics.json` match the values reported in `README.md` and the slide deck.

## Reproducibility note

The notebooks are generated from `scripts/create_training_notebooks.mjs`. If a judge needs to inspect the source of truth for the data-cleaning, feature-engineering, training, and explanation logic, that single file contains all of it - the notebooks themselves are deterministic re-emissions.
