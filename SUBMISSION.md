# Submission Checklist

Biohackathon 2026 submission package for **PCOS Pathfinder**.

## Include in the submission

- `README.md` — quickstart and results snapshot (now headlines bootstrap CIs and the paired AUC test).
- `PROJECT_PLAN.md` — full design rationale.
- `requirements.txt` — pinned dependencies for reproducibility (includes `tabpfn<7` and `pymupdf` in addition to the base stack).
- `notebooks/` — **thirteen** numbered analysis notebooks plus `notebooks/README.md`.
  - 01–06: base pipeline (data audit, screening model, enhanced model, endometriosis overlap, SHAP/demo, single-cell peek).
  - 07: bootstrap CIs and paired AUC-difference test.
  - 08: calibration (Brier, ECE, Platt, isotonic).
  - 09: decision-curve analysis (net benefit).
  - 10: TabPFN-v2 benchmark (Hollmann et al., *Nature* 2025).
  - 11: subgroup fairness audit by age and BMI.
  - 12: split-conformal prediction sets.
  - 13: Rotterdam-criteria clinical-rule benchmark (Teede et al., *Fertil Steril* 2023).
- `outputs/`
  - `figures/` — all plots referenced in the deck and the report (28+ PNGs).
  - `metrics/` — CSV/JSON exports for held-out metrics, threshold trade-offs, SHAP, single-cell gene overlap, **bootstrap CIs, calibration tables, DCA grids, TabPFN comparison, subgroup performance, conformal coverage, Rotterdam comparison**.
  - `models/` — joblib artifacts (screening, enhanced, endometriosis overlap; both PCOS artifacts ship a SHAP background).
  - `pcos_cleaned.csv` — processed PCOS table emitted by notebook 01.
- `scripts/`
  - `create_training_notebooks.mjs` — deterministic regenerator for notebooks 01–06.
  - `build_notebook_09.py` and `build_notebook_10.py` — nbformat builders for the two notebooks that needed a Python builder rather than the JS template.
- `src/app.py` — Streamlit prototype.
- `report/`
  - `build_pdf.py` — reportlab generator for the 15-page technical report.
  - `pcos_pathfinder_report.tex` — parallel LaTeX source.
  - `pcos_pathfinder_report.pdf` — the rendered report.
- The final slide deck (PPTX or PDF) and any speaker notes.

## Exclude from the submission

- `_read_extract/` and `OneDrive_*.zip` — source datasets provided by the organisers; do **not** redistribute unless they explicitly ask for them.
- Large single-cell archives (`*.tar`, `*.tar.gz`) inside `_read_extract/single_cell_peek/`.
- Local virtual environments (`.venv/`, `venv/`).
- Editor / OS junk (`.vscode/`, `.idea/`, `.DS_Store`).
- Notebook checkpoints (`.ipynb_checkpoints/`).
- The `.claude/` directory and its worktrees.

The provided `.gitignore` covers all of the above.

## Pre-submission sanity checks

1. `pip install -r requirements.txt` succeeds on a fresh environment.
2. `node scripts/create_training_notebooks.mjs` regenerates notebooks 01–06 without errors.
3. All 13 notebooks execute end-to-end:
   ```bash
   for nb in notebooks/*.ipynb; do
     python -m nbconvert --to notebook --execute --inplace "$nb"
   done
   ```
4. `streamlit run src/app.py` launches and renders the patient-assessment tab.
5. Model artifacts under `outputs/models/` are present and load via `joblib.load`.
6. Held-out metrics in `outputs/metrics/{screening,enhanced,endometriosis}_holdout_metrics.json` match the values reported in `README.md` and the slide deck.
7. `python report/build_pdf.py` regenerates the PDF cleanly (15 pages, ~1.5 MB).
8. Bootstrap CIs in `outputs/metrics/holdout_bootstrap_cis.json`, calibration in `calibration.json`, DCA in `dca.json`, TabPFN in `tabpfn_comparison.json`, subgroup in `subgroup_performance.json`, conformal in `conformal_coverage.json`, Rotterdam in `rotterdam_comparison.json` — every file present and non-empty.

## Reproducibility note

Notebooks 01–06 are generated from `scripts/create_training_notebooks.mjs`. Notebooks 07–13 are nbformat-built standalone analyses that depend on the model artifacts from notebooks 02 and 03. The `.mjs` file is the source of truth for the base pipeline; notebooks 07–13 are the source of truth for the methodology rigor layer. The report PDF is built from `report/build_pdf.py`.
