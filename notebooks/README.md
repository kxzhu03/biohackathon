# Training Notebooks

Thirteen notebooks. The first six are deterministically regenerated from `scripts/create_training_notebooks.mjs`; notebooks 07–13 are nbformat-built standalone analyses that depend on the saved artifacts from 02 and 03.

## Run order

**Base pipeline (notebooks 01–06 are generated from the .mjs):**

1. `01_pcos_data_audit_and_eda.ipynb` – load, clean, audit, save processed CSV.
2. `02_train_pcos_screening_model.ipynb` – low-cost primary-care screening model.
3. `03_train_pcos_enhanced_model.ipynb` – diagnostic-support model with labs and ultrasound.
4. `04_train_endometriosis_overlap_model.ipynb` – differential-diagnosis prompt (synthetic data).
5. `05_thresholds_explainability_and_demo.ipynb` – SHAP, held-out demo cases, model card.
6. `06_single_cell_gene_peek.ipynb` – optional biological-rationale gene-list check.

**Methodology rigor layer (independent, run after 02/03):**

7. `07_uncertainty_quantification.ipynb` – 2000-resample bootstrap 95% CIs for every held-out metric, paired AUC-difference test (enhanced vs screening).
8. `08_calibration_analysis.ipynb` – Brier, ECE, Platt and isotonic recalibration; reliability diagrams. (Van Calster et al., *BMC Med* 2019)
9. `09_decision_curve_analysis.ipynb` – Net-benefit curves vs `treat-all` / `treat-none` baselines. (Vickers & Elkin, 2006)
10. `10_tabpfn_benchmark.ipynb` – TabPFN-v2 transformer foundation model (Hollmann et al., *Nature* 2025) vs Random Forest.
11. `11_subgroup_fairness.ipynb` – Recall by age band and BMI category with bootstrap CIs. (Obermeyer et al., *Science* 2019)
12. `12_conformal_prediction.ipynb` – Split-conformal prediction sets with empirical-coverage check. (Angelopoulos & Bates, 2023)
13. `13_rotterdam_alignment.ipynb` – Hand-coded Rotterdam 2-of-3 clinical rule vs enhanced ML. (Teede et al., *Fertil Steril* 2023)

## Outputs

- `outputs/figures/` – plots used in the deck and the technical report.
- `outputs/metrics/` – CSV and JSON metric exports (including bootstrap CIs, calibration tables, DCA grids, fairness summaries, conformal coverage, Rotterdam comparison, TabPFN benchmark).
- `outputs/models/` – joblib model artifacts (screening + enhanced + endometriosis-overlap; both PCOS artifacts include a SHAP background).

The notebooks expect either the extracted files in `_read_extract/` or the original `OneDrive_1_5-11-2026.zip` at the project root.

## Install

```bash
pip install -r ../requirements.txt
```
