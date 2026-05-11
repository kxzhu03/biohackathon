# PCOS Pathfinder

A tiered clinical decision-support prototype for earlier PCOS detection and differential diagnosis, built for **Biohackathon 2026: Women's Health** (11-22 May 2026).

## What it does

| Tier | Use case | Inputs | Output |
|---|---|---|---|
| **Screening** | Primary care, telehealth, community clinics | Symptoms + basic vitals (no labs) | High-recall PCOS risk flag |
| **Enhanced** | After labs and ultrasound | Screening features + hormonal panel + follicle/endometrium ultrasound | Diagnostic-support score |
| **Endometriosis overlap** | Differential prompt | Pain, infertility, menstrual irregularity, BMI | Workflow nudge to broaden the differential |

All three are decision support, **not** standalone diagnostic devices.

## Quickstart

```bash
pip install -r requirements.txt
```

Then run the notebooks in order:

1. [`notebooks/01_pcos_data_audit_and_eda.ipynb`](notebooks/01_pcos_data_audit_and_eda.ipynb) - load, clean, audit, save processed CSV.
2. [`notebooks/02_train_pcos_screening_model.ipynb`](notebooks/02_train_pcos_screening_model.ipynb) - low-cost primary-care model.
3. [`notebooks/03_train_pcos_enhanced_model.ipynb`](notebooks/03_train_pcos_enhanced_model.ipynb) - labs + ultrasound model.
4. [`notebooks/04_train_endometriosis_overlap_model.ipynb`](notebooks/04_train_endometriosis_overlap_model.ipynb) - synthetic-data differential prompt.
5. [`notebooks/05_thresholds_explainability_and_demo.ipynb`](notebooks/05_thresholds_explainability_and_demo.ipynb) - SHAP, holdout demo cases, model card.
6. [`notebooks/06_single_cell_gene_peek.ipynb`](notebooks/06_single_cell_gene_peek.ipynb) - optional biological-rationale slide.

Launch the Streamlit prototype:

```bash
streamlit run src/app.py
```

The notebooks accept either the extracted files in `_read_extract/` or the original `OneDrive_1_5-11-2026.zip` in the project root.

## Repository layout

```
biohackathon/
  _read_extract/              # source datasets (extracted from the OneDrive zip)
  notebooks/                  # numbered analysis notebooks (01-06)
  outputs/
    figures/                  # plots referenced by the slide deck
    metrics/                  # CSV/JSON metric exports + model card
    models/                   # joblib model artifacts
  scripts/
    create_training_notebooks.mjs   # regenerates notebooks deterministically
  src/
    app.py                    # Streamlit prototype
  PROJECT_PLAN.md             # full design document
  README.md                   # this file
  requirements.txt
```

## Methodology highlights

- **Threshold selection without test leakage.** Action thresholds are chosen on out-of-fold cross-validation probabilities from the training set, targeting recall ≥ 0.90. The held-out test split is touched once, for final reporting.
- **Threshold-aware risk tiers.** "Low", "Moderate", and "High" labels are anchored to each model's threshold so the tier never contradicts the prediction.
- **Honest demo cases.** Notebook 05 reproduces the train/test split with the same seed and pulls demo patients from the **test** slice, so explanations describe rows the model never trained on.
- **SHAP attributions.** Every demo prediction comes with per-feature log-odds contributions (TreeExplainer for tree models, LinearExplainer for logistic regression).
- **Dropped features.** `blood_group` (meaningless ordinal codes), `marriage_status_yrs` (clinically sensitive, no diagnostic signal), and lifestyle proxies (`fast_food`, `reg_exercise`) are excluded from the screening feature set to avoid bias and stigma.

## Results snapshot

(Held-out test split, n=136, evaluated once at the CV-selected threshold.)

| Model | Threshold | ROC-AUC | Recall | Specificity | F1 |
|---|---|---|---|---|---|
| Screening | 0.285 | 0.896 | 0.886 | 0.685 | 0.696 |
| Enhanced | 0.380 | 0.953 | 0.886 | 0.902 | 0.848 |
| Endometriosis overlap (synthetic) | 0.510 | 0.660 | 0.628 | 0.618 | 0.576 |

The endometriosis model performs at the level expected from the synthetic dataset and is used only as a workflow prompt.

## Important caveats

- The PCOS dataset is single-source (10 hospitals, Kerala, India; n=541). External validation is required before any clinical deployment.
- The endometriosis dataset is synthetic; the overlap module prompts further workup rather than offering a diagnosis.
- Demographic equity variables (race, income, access to care) are not available, so equity claims are based on workflow design and low-resource feasibility, not measured outcome disparities.

See [`PROJECT_PLAN.md`](PROJECT_PLAN.md) for the full design rationale and slide outline.
