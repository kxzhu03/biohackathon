# PCOS Pathfinder

A tiered, explainable clinical decision-support prototype for earlier PCOS detection and differential diagnosis, built for **Biohackathon 2026: Women's Health** (11–22 May 2026).

## What it does

| Tier | Use case | Inputs | Output |
|---|---|---|---|
| **Screening** | Primary care, telehealth, community clinics | Symptoms + basic vitals (no labs) | High-recall PCOS risk flag |
| **Enhanced** | After labs and ultrasound | Screening features + hormonal panel + follicle / endometrium ultrasound | Diagnostic-support score |
| **Endometriosis overlap** | Differential prompt | Pain, infertility, menstrual irregularity, BMI | Workflow nudge to broaden the differential |

All three are decision support, **not** standalone diagnostic devices.

## Quickstart

```bash
pip install -r requirements.txt
```

Run the **base pipeline** in order:

1. [`notebooks/01_pcos_data_audit_and_eda.ipynb`](notebooks/01_pcos_data_audit_and_eda.ipynb) – load, clean, audit, save processed CSV.
2. [`notebooks/02_train_pcos_screening_model.ipynb`](notebooks/02_train_pcos_screening_model.ipynb) – low-cost primary-care model.
3. [`notebooks/03_train_pcos_enhanced_model.ipynb`](notebooks/03_train_pcos_enhanced_model.ipynb) – labs + ultrasound model.
4. [`notebooks/04_train_endometriosis_overlap_model.ipynb`](notebooks/04_train_endometriosis_overlap_model.ipynb) – synthetic-data differential prompt.
5. [`notebooks/05_thresholds_explainability_and_demo.ipynb`](notebooks/05_thresholds_explainability_and_demo.ipynb) – SHAP, held-out demo cases, model card.
6. [`notebooks/06_single_cell_gene_peek.ipynb`](notebooks/06_single_cell_gene_peek.ipynb) – optional biological-rationale slide.

Then run the **methodology rigor layer** (independent of each other, depend on 02 + 03):

7. [`notebooks/07_uncertainty_quantification.ipynb`](notebooks/07_uncertainty_quantification.ipynb) – bootstrap 95% CIs and paired AUC-difference test.
8. [`notebooks/08_calibration_analysis.ipynb`](notebooks/08_calibration_analysis.ipynb) – Brier, ECE, Platt and isotonic recalibration.
9. [`notebooks/09_decision_curve_analysis.ipynb`](notebooks/09_decision_curve_analysis.ipynb) – net-benefit curves vs `treat-all` / `treat-none` baselines.
10. [`notebooks/10_tabpfn_benchmark.ipynb`](notebooks/10_tabpfn_benchmark.ipynb) – TabPFN-v2 (Hollmann et al., *Nature* 2025) vs Random Forest.
11. [`notebooks/11_subgroup_fairness.ipynb`](notebooks/11_subgroup_fairness.ipynb) – recall by age band and BMI category with bootstrap CIs.
12. [`notebooks/12_conformal_prediction.ipynb`](notebooks/12_conformal_prediction.ipynb) – split-conformal prediction sets with empirical-coverage check.
13. [`notebooks/13_rotterdam_alignment.ipynb`](notebooks/13_rotterdam_alignment.ipynb) – Rotterdam 2-of-3 clinical rule vs enhanced ML (Teede et al. 2023).

Launch the Streamlit prototype:

```bash
streamlit run src/app.py
```

Build the technical report PDF:

```bash
python report/build_pdf.py
```

The notebooks accept either the extracted files in `_read_extract/` or the original `OneDrive_1_5-11-2026.zip` in the project root.

## Repository layout

```
biohackathon/
  _read_extract/              # source datasets (extracted from the OneDrive zip)
  notebooks/                  # 13 numbered analysis notebooks (01–13)
  outputs/
    figures/                  # plots referenced by the slide deck and the report
    metrics/                  # CSV/JSON metric exports, model card, audit reports
    models/                   # joblib model artifacts (with SHAP backgrounds)
  scripts/
    create_training_notebooks.mjs   # regenerates notebooks 01–06 deterministically
    build_notebook_09.py            # nbformat builder for notebook 09
    build_notebook_10.py            # nbformat builder for notebook 10
  src/
    app.py                    # Streamlit prototype
  report/
    build_pdf.py              # reportlab generator for the technical report PDF
    pcos_pathfinder_report.tex   # parallel LaTeX source
    pcos_pathfinder_report.pdf
  PROJECT_PLAN.md             # full design document
  SUBMISSION.md               # packaging checklist
  README.md                   # this file
  requirements.txt
```

## Methodology highlights

- **Threshold selection without test leakage.** Action thresholds are chosen on out-of-fold cross-validation probabilities from the training set, targeting recall ≥ 0.90. The held-out test split is touched once, for final reporting.
- **Threshold-aware risk tiers.** *Low*, *Moderate*, and *High* labels are anchored to each model's threshold so the tier never contradicts the prediction.
- **Honest demo cases.** Notebook 05 reproduces the train/test split with the same seed and pulls demo patients from the **test** slice, so explanations describe rows the model never trained on.
- **SHAP attributions.** Every demo prediction comes with per-feature log-odds contributions (TreeExplainer for tree models, LinearExplainer for logistic regression).
- **Bootstrap CIs and paired AUC test.** TRIPOD+AI-style reporting: every held-out metric has 95% percentile CIs from 2000 resamples; the enhanced vs screening AUC comparison uses a paired bootstrap test.
- **Calibration + conformal coverage.** Platt scaling improves enhanced Brier from 0.093 → 0.072 and ECE from 0.143 → 0.045; split-conformal hits empirical coverage 0.912 against target 0.90.
- **Decision Curve Analysis.** Both action thresholds sit inside their useful net-benefit ranges.
- **External benchmarks.** TabPFN-v2 (Nature 2025) confirms our Random Forest is near-ceiling on this dataset (Δ AUC < +0.01); compared with a hand-coded Rotterdam 2-of-3 rule (Teede et al. 2023), the enhanced ML model adds 9.1 pts sensitivity with a 1.1 pt specificity cost.
- **Fairness audit.** Subgroup recall reported by age band and BMI category with bootstrap CIs. A 25-point BMI recall gap in the screening model is flagged honestly as a deployment risk.
- **Diagnostic workflow checks.** The Streamlit app now shows a Rotterdam-style completeness checklist, missing-test caveat, metabolic follow-up prompt, and lean-PCOS safety warning.
- **Dropped / excluded features.** `blood_group` is excluded from current model inputs because its 11-18 codes are categorical ABO/Rh labels, not an ordered scale; validated blood group should be kept as categorical metadata for future symptom-severity/subgroup displays. `marriage_status_yrs` is clinically sensitive with no diagnostic signal, and lifestyle proxies (`fast_food`, `reg_exercise`) are excluded from screening to avoid bias and stigma.

## Results snapshot

Held-out test split (n=136). Numbers in brackets are 2000-resample bootstrap 95% percentile CIs.

| Model | Threshold | ROC-AUC | Recall | Specificity | NPV | F2 |
|---|---|---|---|---|---|---|
| Screening | 0.285 | 0.896 [0.830, 0.951] | 0.886 [0.787, 0.975] | 0.685 | 0.926 | 0.799 |
| Enhanced | 0.380 | **0.953 [0.911, 0.985]** | 0.886 [0.786, 0.974] | 0.902 | 0.943 | 0.871 |
| Endometriosis overlap (synthetic) | 0.510 | 0.660 | 0.628 | 0.618 | — | 0.609 |

**Paired bootstrap AUC test (enhanced vs screening):** ΔAUC = +0.057, 95% CI [+0.013, +0.105], two-sided p ≈ 0.015 — the enhanced model appears better on this held-out split, not merely numerically different.

## Important caveats

- The PCOS dataset is single-source (10 hospitals, Kerala, India; n=541). External validation is required before any clinical deployment.
- The endometriosis dataset is synthetic; the overlap module prompts further workup rather than offering a diagnosis.
- Demographic equity variables (race, income, access to care) are not available; the fairness audit uses only age and BMI.
- The screening model has a 25-point recall gap by BMI on the held-out cohort, narrowing to 20 points in the enhanced model. We flag this as a deployment risk in the model card.

See [`PROJECT_PLAN.md`](PROJECT_PLAN.md) for the full design rationale and [`report/pcos_pathfinder_report.pdf`](report/pcos_pathfinder_report.pdf) for the 15-page technical report.
