# Training Notebooks

Run order:

1. `01_pcos_data_audit_and_eda.ipynb` - load, clean, audit, save processed CSV.
2. `02_train_pcos_screening_model.ipynb` - low-cost primary-care screening model.
3. `03_train_pcos_enhanced_model.ipynb` - diagnostic-support model with labs and ultrasound.
4. `04_train_endometriosis_overlap_model.ipynb` - differential-diagnosis prompt (synthetic data).
5. `05_thresholds_explainability_and_demo.ipynb` - SHAP, holdout demo cases, model card.
6. `06_single_cell_gene_peek.ipynb` - optional biological rationale slide.

Outputs land in:

- `outputs/figures/` - plots used in the deck.
- `outputs/metrics/` - CSV and JSON metric exports.
- `outputs/models/` - joblib model artifacts.

They expect either the extracted files in `_read_extract/` or the original `OneDrive_1_5-11-2026.zip` in the project root.

Install dependencies with:

```bash
pip install -r requirements.txt
```
