
# PCOS Pathfinder Model Card

## Intended use

Decision support for PCOS risk screening and diagnostic triage. **Not** a standalone diagnostic device.

## Data

- Required PCOS clinical dataset (10 hospitals, Kerala, India).
- Cleaned rows: 541
- PCOS-positive: 177 | PCOS-negative: 364
- Columns dropped during cleaning: ['sl_no', 'patient_file_no', 'blood_group', 'marriage_status_yrs']

## Models

### Screening model

- Algorithm: random_forest
- Features: 13 (no lifestyle proxies)
- Threshold: 0.285 (chosen on training CV at recall>=0.90)
- Holdout ROC-AUC: 0.896
- Holdout recall / specificity: 0.886 / 0.685

### Enhanced model

- Algorithm: random_forest
- Features: 27
- Threshold: 0.380 (chosen on training CV at recall>=0.90)
- Holdout ROC-AUC: 0.953
- Holdout recall / specificity: 0.886 / 0.902

## Explainability

- Global: tree feature importances or scaled logistic-regression coefficients.
- Local: SHAP attributions for each prediction.

## Limitations

- Single-source geography (Kerala, India); generalisation requires external validation.
- Small dataset (541 rows).
- Endometriosis overlap module uses synthetic data and only prompts further workup.
- Demographic equity variables (race, income, access to care) are not available.
- Outputs must be combined with clinical judgement.
