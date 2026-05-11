import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const notebooksDir = path.join(root, "notebooks");
const outputsDir = path.join(root, "outputs");
const modelsDir = path.join(outputsDir, "models");
const figuresDir = path.join(outputsDir, "figures");
const metricsDir = path.join(outputsDir, "metrics");

for (const dir of [notebooksDir, outputsDir, modelsDir, figuresDir, metricsDir]) {
  fs.mkdirSync(dir, { recursive: true });
}

const nb = (cells) => ({
  cells,
  metadata: {
    kernelspec: {
      display_name: "Python 3",
      language: "python",
      name: "python3",
    },
    language_info: {
      name: "python",
      version: "3.11",
      mimetype: "text/x-python",
      codemirror_mode: { name: "ipython", version: 3 },
      pygments_lexer: "ipython3",
      nbconvert_exporter: "python",
      file_extension: ".py",
    },
  },
  nbformat: 4,
  nbformat_minor: 5,
});

const lines = (text) => text.replace(/\r\n/g, "\n").split("\n").map((line) => `${line}\n`);
const md = (text) => ({ cell_type: "markdown", metadata: {}, source: lines(text.trim()) });
const code = (text) => ({ cell_type: "code", execution_count: null, metadata: {}, outputs: [], source: lines(text.trim()) });

const commonSetup = String.raw`
from pathlib import Path
import re
import json
import warnings
import zipfile

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110

RANDOM_STATE = 42

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
RAW_DIR = PROJECT_ROOT / "_read_extract"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"
MODEL_DIR = OUTPUT_DIR / "models"
METRIC_DIR = OUTPUT_DIR / "metrics"

for folder in [RAW_DIR, OUTPUT_DIR, FIGURE_DIR, MODEL_DIR, METRIC_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

ZIP_PATH = PROJECT_ROOT / "OneDrive_1_5-11-2026.zip"
PCOS_XLSX = RAW_DIR / "(Main_Dataset)_PCOS_data_without_infertility.xlsx"
ENDO_CSV = RAW_DIR / "(Supplementary_Dataset)_structured_endometriosis_data.csv"

def ensure_small_datasets_extracted():
    """Extract only the tabular datasets if they are not already available."""
    if PCOS_XLSX.exists() and ENDO_CSV.exists():
        return
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Cannot find {ZIP_PATH}")
    targets = {
        "(Main_Dataset)_PCOS_data_without_infertility.xlsx": PCOS_XLSX,
        "(Supplementary_Dataset)_structured_endometriosis_data.csv": ENDO_CSV,
    }
    with zipfile.ZipFile(ZIP_PATH) as zf:
        for member, destination in targets.items():
            if not destination.exists():
                with zf.open(member) as src, open(destination, "wb") as dst:
                    dst.write(src.read())

ensure_small_datasets_extracted()

def clean_column_name(name):
    name = str(name).strip().lower()
    name = name.replace("β", "beta")
    name = name.replace("marraige", "marriage")
    name = name.replace("bp _", "bp ")
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name

# Columns we never want to keep, even though they parse as numeric.
# - sl_no / patient_file_no: identifiers, no clinical signal.
# - blood_group: stored as ordinal codes (11-18) which has no meaningful order.
# - marriage_status_yrs: clinically sensitive and a poor proxy for anything
#   diagnostic; the plan flags it as unsuitable for screening.
DROP_COLUMNS = ["sl_no", "patient_file_no", "blood_group", "marriage_status_yrs"]

def load_pcos_raw():
    df = pd.read_excel(PCOS_XLSX, sheet_name="Full_new", engine="openpyxl")
    df = df.dropna(how="all").copy()
    df.columns = [clean_column_name(c) for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated()].copy()
    return df

def clean_pcos_dataframe(df):
    df = df.copy()

    # Track silently-coerced non-numeric cells so the audit can flag them.
    coercion_report = {}
    for col in df.columns:
        before_non_null = df[col].notna().sum()
        coerced = pd.to_numeric(df[col], errors="coerce")
        new_nan = coerced.isna().sum() - df[col].isna().sum()
        if new_nan > 0:
            offending = df.loc[df[col].notna() & coerced.isna(), col].astype(str).unique().tolist()
            coercion_report[col] = {"coerced_to_nan": int(new_nan), "examples": offending[:5]}
        df[col] = coerced

    drop_now = [c for c in DROP_COLUMNS if c in df.columns]
    df = df.drop(columns=drop_now)

    if "pcos_y_n" not in df.columns:
        raise ValueError("Expected target column 'pcos_y_n' after cleaning column names.")

    df = df[df["pcos_y_n"].isin([0, 1])].copy()
    df["pcos_y_n"] = df["pcos_y_n"].astype(int)

    # Kaggle-style encoding uses 2 for regular and 4/5 for irregular cycles.
    if "cycle_r_i" in df.columns:
        df["cycle_irregular_flag"] = np.where(
            df["cycle_r_i"].isna(),
            np.nan,
            np.where(df["cycle_r_i"] >= 4, 1, 0),
        )

    # Conservative caps for visibly impossible or model-dominating outliers.
    caps = {
        "fsh_miu_ml": (0, 100),
        "lh_miu_ml": (0, 200),
        "fsh_lh": (0, 50),
        "vit_d3_ng_ml": (0, 150),
        "prg_ng_ml": (0, 50),
    }
    for col, (low, high) in caps.items():
        if col in df.columns:
            df[col] = df[col].clip(lower=low, upper=high)

    df.attrs["coercion_report"] = coercion_report
    df.attrs["dropped_columns"] = drop_now
    return df

pcos_raw = load_pcos_raw()
pcos = clean_pcos_dataframe(pcos_raw)
print("PCOS shape:", pcos.shape)
print("Dropped columns:", pcos.attrs["dropped_columns"])
if pcos.attrs["coercion_report"]:
    print("Non-numeric values coerced to NaN:")
    for col, info in pcos.attrs["coercion_report"].items():
        print(f"  {col}: {info['coerced_to_nan']} cell(s); examples={info['examples']}")
print(pcos["pcos_y_n"].value_counts().sort_index())
`;

const featureHelpers = String.raw`
TARGET = "pcos_y_n"

# fast_food_y_n and reg_exercise_y_n are deliberately excluded.
# The plan flags lifestyle proxies as bias-prone and likely to stigmatise patients.
SCREENING_FEATURES = [
    "age_yrs",
    "bmi",
    "cycle_r_i",
    "cycle_irregular_flag",
    "cycle_length_days",
    "weight_gain_y_n",
    "hair_growth_y_n",
    "skin_darkening_y_n",
    "hair_loss_y_n",
    "pimples_y_n",
    "rbs_mg_dl",
    "bp_systolic_mmhg",
    "bp_diastolic_mmhg",
]

ENHANCED_EXTRA_FEATURES = [
    "hb_g_dl",
    "fsh_miu_ml",
    "lh_miu_ml",
    "fsh_lh",
    "tsh_miu_l",
    "amh_ng_ml",
    "prl_ng_ml",
    "vit_d3_ng_ml",
    "prg_ng_ml",
    "follicle_no_l",
    "follicle_no_r",
    "avg_f_size_l_mm",
    "avg_f_size_r_mm",
    "endometrium_mm",
]

def available(features, df):
    return [feature for feature in features if feature in df.columns]

screening_features = available(SCREENING_FEATURES, pcos)
enhanced_features = available(SCREENING_FEATURES + ENHANCED_EXTRA_FEATURES, pcos)

print("Screening features:", screening_features)
print("Enhanced features:", enhanced_features)
`;

const sklearnImports = String.raw`
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_predict,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib
`;

const trainingFunctions = String.raw`
def make_models():
    return {
        "dummy_most_frequent": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", DummyClassifier(strategy="most_frequent")),
        ]),
        "logistic_regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE)),
        ]),
        "random_forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(
                n_estimators=500,
                min_samples_leaf=4,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            )),
        ]),
        "gradient_boosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", GradientBoostingClassifier(random_state=RANDOM_STATE)),
        ]),
    }

SCORING = {
    "roc_auc": "roc_auc",
    "recall": "recall",
    "precision": "precision",
    "f1": "f1",
    "balanced_accuracy": "balanced_accuracy",
}

def cross_validate_models(X, y, models, n_splits=5):
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    rows = []
    for name, model in models.items():
        scores = cross_validate(model, X, y, cv=cv, scoring=SCORING, n_jobs=-1, error_score="raise")
        row = {"model": name}
        for metric in SCORING:
            row[f"{metric}_mean"] = scores[f"test_{metric}"].mean()
            row[f"{metric}_std"] = scores[f"test_{metric}"].std()
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["roc_auc_mean", "recall_mean"], ascending=False)

def cv_oof_probabilities(model, X, y, n_splits=5):
    """Out-of-fold positive-class probabilities for threshold tuning without leakage."""
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    return cross_val_predict(model, X, y, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]

def evaluate_holdout(model, X_test, y_test, threshold=0.5):
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= threshold).astype(int)
    return {
        "threshold": threshold,
        "roc_auc": roc_auc_score(y_test, proba),
        "recall": recall_score(y_test, pred),
        "specificity": recall_score(y_test, pred, pos_label=0),
        "precision": precision_score(y_test, pred, zero_division=0),
        "f1": f1_score(y_test, pred),
        "balanced_accuracy": balanced_accuracy_score(y_test, pred),
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
    }

def choose_high_recall_threshold(y_true, y_proba, min_recall=0.90):
    thresholds = np.round(np.linspace(0.05, 0.95, 181), 3)
    rows = []
    for threshold in thresholds:
        pred = (y_proba >= threshold).astype(int)
        rows.append({
            "threshold": threshold,
            "recall": recall_score(y_true, pred),
            "specificity": recall_score(y_true, pred, pos_label=0),
            "precision": precision_score(y_true, pred, zero_division=0),
            "f1": f1_score(y_true, pred),
            "balanced_accuracy": balanced_accuracy_score(y_true, pred),
        })
    table = pd.DataFrame(rows)
    candidates = table[table["recall"] >= min_recall]
    if len(candidates):
        chosen = candidates.sort_values(["specificity", "precision", "f1"], ascending=False).iloc[0]
    else:
        chosen = table.sort_values(["f1", "balanced_accuracy"], ascending=False).iloc[0]
    return chosen, table

def make_risk_tier(threshold):
    """Risk tiers anchored to the model's action threshold so labels never contradict predictions."""
    high_cutoff = min(0.90, threshold + 0.20)
    def risk_tier(probability):
        if probability < threshold:
            return "Low"
        if probability < high_cutoff:
            return "Moderate"
        return "High"
    return risk_tier

def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
`;

const notebook01 = nb([
  md(`# 01 - PCOS Data Audit and EDA

Purpose:

- Load the required PCOS clinical dataset.
- Clean the raw workbook into an analysis-ready table.
- Audit missingness, class balance, outliers, and silently coerced values.
- Save a processed CSV for later notebooks.

Run this notebook first.`),
  code(`${commonSetup}`),
  md(`## Save Processed Dataset`),
  code(String.raw`
processed_path = OUTPUT_DIR / "pcos_cleaned.csv"
pcos.to_csv(processed_path, index=False)
print("Saved:", processed_path)
pcos.head()
`),
  md(`## Column Audit`),
  code(String.raw`
audit = pd.DataFrame({
    "column": pcos.columns,
    "dtype": [str(pcos[c].dtype) for c in pcos.columns],
    "missing": [pcos[c].isna().sum() for c in pcos.columns],
    "missing_pct": [pcos[c].isna().mean() for c in pcos.columns],
    "n_unique": [pcos[c].nunique(dropna=True) for c in pcos.columns],
})
audit.to_csv(METRIC_DIR / "pcos_column_audit.csv", index=False)
audit
`),
  md(`## Data Quality Issues Coerced During Cleaning

Non-numeric strings in numeric columns silently become NaN. These are logged for the slide-deck data-quality discussion.`),
  code(String.raw`
coercion_report = pcos.attrs.get("coercion_report", {})
if coercion_report:
    coercion_df = pd.DataFrame([
        {"column": col, "coerced_to_nan": info["coerced_to_nan"], "examples": ", ".join(info["examples"])}
        for col, info in coercion_report.items()
    ])
    coercion_df.to_csv(METRIC_DIR / "pcos_coercion_report.csv", index=False)
    display(coercion_df)
else:
    print("No non-numeric values were coerced.")
print("Columns intentionally dropped:", pcos.attrs.get("dropped_columns", []))
`),
  md(`## Class Balance`),
  code(String.raw`
class_counts = pcos["pcos_y_n"].value_counts().sort_index()
display(class_counts.rename({0: "non_pcos", 1: "pcos"}))

fig, ax = plt.subplots(figsize=(5, 4))
class_counts.plot(kind="bar", ax=ax, color=["#3a7ca5", "#d95f59"])
ax.set_title("PCOS target distribution")
ax.set_xlabel("PCOS status")
ax.set_ylabel("Patients")
ax.set_xticklabels(["No PCOS", "PCOS"], rotation=0)
fig.tight_layout()
fig.savefig(FIGURE_DIR / "pcos_class_balance.png", dpi=160)
plt.show()
`),
  md(`## Feature Groups`),
  code(`${featureHelpers}`),
  md(`## Summary Statistics by PCOS Status`),
  code(String.raw`
summary_features = [
    "age_yrs", "bmi", "cycle_r_i", "cycle_irregular_flag", "cycle_length_days",
    "fsh_miu_ml", "lh_miu_ml", "fsh_lh", "amh_ng_ml", "rbs_mg_dl",
    "follicle_no_l", "follicle_no_r", "endometrium_mm",
]
summary_features = available(summary_features, pcos)
summary = pcos.groupby("pcos_y_n")[summary_features].agg(["mean", "median", "std"]).T
summary.to_csv(METRIC_DIR / "pcos_grouped_summary.csv")
summary
`),
  md(`## Symptom Prevalence by PCOS Status`),
  code(String.raw`
symptom_cols = available([
    "weight_gain_y_n", "hair_growth_y_n", "skin_darkening_y_n",
    "hair_loss_y_n", "pimples_y_n", "reg_exercise_y_n",
], pcos)

symptom_rates = pcos.groupby("pcos_y_n")[symptom_cols].mean().T
symptom_rates.columns = ["non_pcos_rate", "pcos_rate"]
symptom_rates["absolute_difference"] = symptom_rates["pcos_rate"] - symptom_rates["non_pcos_rate"]
symptom_rates = symptom_rates.sort_values("absolute_difference", ascending=False)
symptom_rates.to_csv(METRIC_DIR / "pcos_symptom_rates.csv")
display(symptom_rates)

fig, ax = plt.subplots(figsize=(8, 5))
symptom_rates[["non_pcos_rate", "pcos_rate"]].plot(kind="barh", ax=ax)
ax.set_title("Symptom rates by PCOS status")
ax.set_xlabel("Rate")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "pcos_symptom_rates.png", dpi=160)
plt.show()
`),
  md(`## Outlier Review`),
  code(String.raw`
outlier_cols = available([
    "fsh_miu_ml", "lh_miu_ml", "fsh_lh", "vit_d3_ng_ml", "prg_ng_ml",
    "i_beta_hcg_miu_ml", "ii_beta_hcg_miu_ml",
], pcos)

outlier_table = pcos[outlier_cols].describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).T
outlier_table.to_csv(METRIC_DIR / "pcos_outlier_review.csv")
outlier_table
`),
  md(`## Correlation Snapshot`),
  code(String.raw`
numeric = pcos.select_dtypes(include=[np.number])
top_corr = numeric.corr(numeric_only=True)["pcos_y_n"].drop("pcos_y_n").abs().sort_values(ascending=False).head(20)
display(top_corr)

plot_cols = ["pcos_y_n"] + top_corr.index.tolist()[:12]
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(numeric[plot_cols].corr(), cmap="vlag", center=0, ax=ax)
ax.set_title("Correlation heatmap for top PCOS-associated features")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "pcos_correlation_heatmap.png", dpi=160)
plt.show()
`),
]);

const notebook02 = nb([
  md(`# 02 - Train PCOS Screening Model

Purpose:

- Train a low-cost PCOS screening model from features available in primary care and telehealth.
- Choose a high-recall threshold using **cross-validation on the training set** to avoid test leakage.
- Evaluate the final model once on the held-out test split.

Run after notebook 01, or standalone (it re-runs cleaning).`),
  code(`${commonSetup}\n\n${featureHelpers}\n\n${sklearnImports}\n\n${trainingFunctions}`),
  md(`## Prepare Screening Dataset`),
  code(String.raw`
X = pcos[screening_features].copy()
y = pcos[TARGET].copy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    stratify=y,
    random_state=RANDOM_STATE,
)

print("Train:", X_train.shape, "Test:", X_test.shape)
print("Train target balance:")
print(y_train.value_counts(normalize=True).sort_index())
`),
  md(`## Cross-Validate Candidate Models`),
  code(String.raw`
models = make_models()
cv_results = cross_validate_models(X_train, y_train, models)
cv_results.to_csv(METRIC_DIR / "screening_cv_results.csv", index=False)
cv_results
`),
  md(`## Fit Best Screening Model

Threshold is chosen on out-of-fold CV probabilities from the training set, then the model is refit on the full training set and evaluated **once** on the held-out test split.`),
  code(String.raw`
best_name = cv_results.iloc[0]["model"]
best_screening_model = models[best_name]
print("Best screening model:", best_name)

# 1. Out-of-fold probabilities on training data (no leakage).
oof_proba_train = cv_oof_probabilities(best_screening_model, X_train, y_train)
chosen_threshold, threshold_table = choose_high_recall_threshold(y_train, oof_proba_train, min_recall=0.90)
threshold = float(chosen_threshold["threshold"])
threshold_table.to_csv(METRIC_DIR / "screening_threshold_table.csv", index=False)
print("Chosen threshold (from training CV):")
display(chosen_threshold)

# 2. Refit on full training data, then evaluate once on test.
best_screening_model.fit(X_train, y_train)
test_proba = best_screening_model.predict_proba(X_test)[:, 1]

screening_metrics = evaluate_holdout(best_screening_model, X_test, y_test, threshold=threshold)
save_json(screening_metrics, METRIC_DIR / "screening_holdout_metrics.json")
screening_metrics
`),
  md(`## Confusion Matrix and Curves`),
  code(String.raw`
pred = (test_proba >= threshold).astype(int)

fig, ax = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay.from_predictions(y_test, pred, display_labels=["No PCOS", "PCOS"], cmap="Blues", ax=ax)
ax.set_title(f"Screening model confusion matrix at threshold {threshold:.2f}")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "screening_confusion_matrix.png", dpi=160)
plt.show()

fig, ax = plt.subplots(figsize=(5, 4))
RocCurveDisplay.from_predictions(y_test, test_proba, ax=ax)
ax.set_title("Screening model ROC curve")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "screening_roc_curve.png", dpi=160)
plt.show()

fig, ax = plt.subplots(figsize=(5, 4))
PrecisionRecallDisplay.from_predictions(y_test, test_proba, ax=ax)
ax.set_title("Screening model precision-recall curve")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "screening_precision_recall_curve.png", dpi=160)
plt.show()
`),
  md(`## Save Screening Model Artifact`),
  code(String.raw`
background_sample = X_train.sample(min(100, len(X_train)), random_state=RANDOM_STATE)
shap_background = background_sample.copy()
for _, transformer in best_screening_model.steps[:-1]:
    shap_background = transformer.transform(shap_background)

artifact = {
    "model": best_screening_model,
    "model_name": best_name,
    "features": screening_features,
    "target": TARGET,
    "threshold": threshold,
    "threshold_source": "cv_oof_training",
    "metrics": screening_metrics,
    "shap_background_transformed": np.asarray(shap_background),
    "notes": "High-recall PCOS screening model. Use as decision support, not standalone diagnosis.",
}

artifact_path = MODEL_DIR / "pcos_screening_model.joblib"
joblib.dump(artifact, artifact_path)
print("Saved:", artifact_path)
`),
]);

const notebook03 = nb([
  md(`# 03 - Train PCOS Enhanced Diagnostic Model

Purpose:

- Train an enhanced PCOS model using clinical, lab, and ultrasound features.
- Choose a high-recall threshold using cross-validation on training data (no test leakage).
- Compare performance against the screening-only model.

Run after notebook 01, or standalone.`),
  code(`${commonSetup}\n\n${featureHelpers}\n\n${sklearnImports}\n\n${trainingFunctions}`),
  md(`## Prepare Enhanced Dataset`),
  code(String.raw`
X = pcos[enhanced_features].copy()
y = pcos[TARGET].copy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    stratify=y,
    random_state=RANDOM_STATE,
)

print("Enhanced feature count:", len(enhanced_features))
print("Train:", X_train.shape, "Test:", X_test.shape)
`),
  md(`## Cross-Validate Candidate Models`),
  code(String.raw`
models = make_models()
cv_results = cross_validate_models(X_train, y_train, models)
cv_results.to_csv(METRIC_DIR / "enhanced_cv_results.csv", index=False)
cv_results
`),
  md(`## Fit Best Enhanced Model`),
  code(String.raw`
best_name = cv_results.iloc[0]["model"]
best_enhanced_model = models[best_name]
print("Best enhanced model:", best_name)

oof_proba_train = cv_oof_probabilities(best_enhanced_model, X_train, y_train)
chosen_threshold, threshold_table = choose_high_recall_threshold(y_train, oof_proba_train, min_recall=0.90)
threshold = float(chosen_threshold["threshold"])
threshold_table.to_csv(METRIC_DIR / "enhanced_threshold_table.csv", index=False)
print("Chosen threshold (from training CV):")
display(chosen_threshold)

best_enhanced_model.fit(X_train, y_train)
test_proba = best_enhanced_model.predict_proba(X_test)[:, 1]

enhanced_metrics = evaluate_holdout(best_enhanced_model, X_test, y_test, threshold=threshold)
save_json(enhanced_metrics, METRIC_DIR / "enhanced_holdout_metrics.json")
enhanced_metrics
`),
  md(`## Confusion Matrix and Curves`),
  code(String.raw`
pred = (test_proba >= threshold).astype(int)

fig, ax = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay.from_predictions(y_test, pred, display_labels=["No PCOS", "PCOS"], cmap="Purples", ax=ax)
ax.set_title(f"Enhanced model confusion matrix at threshold {threshold:.2f}")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "enhanced_confusion_matrix.png", dpi=160)
plt.show()

fig, ax = plt.subplots(figsize=(5, 4))
RocCurveDisplay.from_predictions(y_test, test_proba, ax=ax)
ax.set_title("Enhanced model ROC curve")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "enhanced_roc_curve.png", dpi=160)
plt.show()

fig, ax = plt.subplots(figsize=(5, 4))
PrecisionRecallDisplay.from_predictions(y_test, test_proba, ax=ax)
ax.set_title("Enhanced model precision-recall curve")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "enhanced_precision_recall_curve.png", dpi=160)
plt.show()
`),
  md(`## Save Enhanced Model Artifact`),
  code(String.raw`
background_sample = X_train.sample(min(100, len(X_train)), random_state=RANDOM_STATE)
shap_background = background_sample.copy()
for _, transformer in best_enhanced_model.steps[:-1]:
    shap_background = transformer.transform(shap_background)

artifact = {
    "model": best_enhanced_model,
    "model_name": best_name,
    "features": enhanced_features,
    "target": TARGET,
    "threshold": threshold,
    "threshold_source": "cv_oof_training",
    "metrics": enhanced_metrics,
    "shap_background_transformed": np.asarray(shap_background),
    "notes": "Enhanced PCOS diagnostic-support model using labs and ultrasound features.",
}

artifact_path = MODEL_DIR / "pcos_enhanced_model.joblib"
joblib.dump(artifact, artifact_path)
print("Saved:", artifact_path)
`),
]);

const notebook04 = nb([
  md(`# 04 - Train Endometriosis Overlap Model

Purpose:

- Train a lightweight model on the supplementary endometriosis dataset.
- Use it as a differential-diagnosis prompt, not a clinical diagnostic model.
- Save a small artifact that can flag endometriosis-like symptom overlap.

Important: the provided endometriosis data is synthetic. Do not present this as externally-validated clinical diagnosis.`),
  code(String.raw`
from pathlib import Path
import re
import json
import warnings
import zipfile

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_predict,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110

RANDOM_STATE = 42

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
RAW_DIR = PROJECT_ROOT / "_read_extract"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"
MODEL_DIR = OUTPUT_DIR / "models"
METRIC_DIR = OUTPUT_DIR / "metrics"

for folder in [RAW_DIR, OUTPUT_DIR, FIGURE_DIR, MODEL_DIR, METRIC_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

ZIP_PATH = PROJECT_ROOT / "OneDrive_1_5-11-2026.zip"
ENDO_CSV = RAW_DIR / "(Supplementary_Dataset)_structured_endometriosis_data.csv"

if not ENDO_CSV.exists():
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Cannot find {ENDO_CSV} or {ZIP_PATH}")
    with zipfile.ZipFile(ZIP_PATH) as zf:
        with zf.open("(Supplementary_Dataset)_structured_endometriosis_data.csv") as src, open(ENDO_CSV, "wb") as dst:
            dst.write(src.read())

def clean_column_name(name):
    name = str(name).strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name

endo = pd.read_csv(ENDO_CSV)
endo.columns = [clean_column_name(c) for c in endo.columns]
for col in endo.columns:
    endo[col] = pd.to_numeric(endo[col], errors="coerce")

endo = endo.dropna(subset=["diagnosis"]).copy()
endo["diagnosis"] = endo["diagnosis"].astype(int)

print("Endometriosis data shape:", endo.shape)
print(endo["diagnosis"].value_counts().sort_index())
endo.head()
`),
  md(`## Train Differential Overlap Classifier`),
  code(String.raw`
TARGET = "diagnosis"
features = [c for c in endo.columns if c != TARGET]
X = endo[features].copy()
y = endo[TARGET].copy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    stratify=y,
    random_state=RANDOM_STATE,
)

models = {
    "dummy_most_frequent": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", DummyClassifier(strategy="most_frequent")),
    ]),
    "logistic_regression": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE)),
    ]),
    "random_forest": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(
            n_estimators=400,
            min_samples_leaf=10,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        )),
    ]),
    "gradient_boosting": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", GradientBoostingClassifier(random_state=RANDOM_STATE)),
    ]),
}

scoring = {
    "roc_auc": "roc_auc",
    "recall": "recall",
    "precision": "precision",
    "f1": "f1",
    "balanced_accuracy": "balanced_accuracy",
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
rows = []
for name, model in models.items():
    scores = cross_validate(model, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)
    row = {"model": name}
    for metric in scoring:
        row[f"{metric}_mean"] = scores[f"test_{metric}"].mean()
        row[f"{metric}_std"] = scores[f"test_{metric}"].std()
    rows.append(row)

cv_results = pd.DataFrame(rows).sort_values(["roc_auc_mean", "recall_mean"], ascending=False)
cv_results.to_csv(METRIC_DIR / "endometriosis_cv_results.csv", index=False)
cv_results
`),
  md(`## Threshold Selection (CV on Training Data)`),
  code(String.raw`
best_name = cv_results.iloc[0]["model"]
best_endo_model = models[best_name]

oof_proba = cross_val_predict(best_endo_model, X_train, y_train, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]

thresholds = np.round(np.linspace(0.05, 0.95, 91), 3)
rows = []
for t in thresholds:
    p = (oof_proba >= t).astype(int)
    rows.append({
        "threshold": t,
        "recall": recall_score(y_train, p),
        "specificity": recall_score(y_train, p, pos_label=0),
        "precision": precision_score(y_train, p, zero_division=0),
        "f1": f1_score(y_train, p),
        "balanced_accuracy": balanced_accuracy_score(y_train, p),
    })
threshold_table = pd.DataFrame(rows)
threshold_table.to_csv(METRIC_DIR / "endometriosis_threshold_table.csv", index=False)

# For a differential-diagnosis *prompt* we want decent precision, not max recall.
chosen = threshold_table.sort_values(["balanced_accuracy", "f1"], ascending=False).iloc[0]
threshold = float(chosen["threshold"])
print("Chosen threshold:", threshold)
display(chosen)
`),
  md(`## Evaluate and Save Artifact`),
  code(String.raw`
best_endo_model.fit(X_train, y_train)
proba = best_endo_model.predict_proba(X_test)[:, 1]
pred = (proba >= threshold).astype(int)

metrics = {
    "model_name": best_name,
    "threshold": threshold,
    "threshold_source": "cv_oof_training",
    "roc_auc": roc_auc_score(y_test, proba),
    "recall": recall_score(y_test, pred),
    "specificity": recall_score(y_test, pred, pos_label=0),
    "precision": precision_score(y_test, pred, zero_division=0),
    "f1": f1_score(y_test, pred),
    "balanced_accuracy": balanced_accuracy_score(y_test, pred),
    "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
    "warning": "Synthetic data. Use only as a symptom-overlap prompt.",
}

with open(METRIC_DIR / "endometriosis_holdout_metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

display(metrics)

fig, ax = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay.from_predictions(y_test, pred, display_labels=["No Endo", "Endo"], cmap="Greens", ax=ax)
ax.set_title("Endometriosis overlap model confusion matrix")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "endometriosis_confusion_matrix.png", dpi=160)
plt.show()

fig, ax = plt.subplots(figsize=(5, 4))
RocCurveDisplay.from_predictions(y_test, proba, ax=ax)
ax.set_title("Endometriosis overlap model ROC curve")
fig.tight_layout()
fig.savefig(FIGURE_DIR / "endometriosis_roc_curve.png", dpi=160)
plt.show()

artifact = {
    "model": best_endo_model,
    "model_name": best_name,
    "features": features,
    "target": TARGET,
    "threshold": threshold,
    "threshold_source": "cv_oof_training",
    "metrics": metrics,
    "notes": "Synthetic endometriosis overlap model. Use only to prompt differential workup.",
}

artifact_path = MODEL_DIR / "endometriosis_overlap_model.joblib"
joblib.dump(artifact, artifact_path)
print("Saved:", artifact_path)
`),
  md(`## Example Overlap Flag Function`),
  code(String.raw`
def endometriosis_overlap_flag(age, menstrual_irregularity, chronic_pain_level, hormone_level_abnormality, infertility, bmi):
    row = pd.DataFrame([{
        "age": age,
        "menstrual_irregularity": menstrual_irregularity,
        "chronic_pain_level": chronic_pain_level,
        "hormone_level_abnormality": hormone_level_abnormality,
        "infertility": infertility,
        "bmi": bmi,
    }])
    probability = best_endo_model.predict_proba(row[features])[:, 1][0]
    if probability >= threshold:
        label = "Endometriosis-overlap pattern: consider broader differential workup."
    else:
        label = "No strong endometriosis-overlap pattern from this simple module."
    return probability, label

endometriosis_overlap_flag(
    age=31,
    menstrual_irregularity=1,
    chronic_pain_level=8,
    hormone_level_abnormality=1,
    infertility=1,
    bmi=24,
)
`),
]);

const notebook05 = nb([
  md(`# 05 - Thresholds, SHAP Explainability, and Demo Cases

Purpose:

- Load saved PCOS models.
- Compare global drivers across screening and enhanced models.
- Compute SHAP-based per-patient explanations.
- Build demo predictions from **held-out** test rows so explanations are honest.
- Emit a model card for the deck.

Run after notebooks 02 and 03.`),
  code(`${commonSetup}\n\n${featureHelpers}\n\n${sklearnImports}\n\n${trainingFunctions}`),
  md(`## Load Saved Artifacts`),
  code(String.raw`
screening_path = MODEL_DIR / "pcos_screening_model.joblib"
enhanced_path = MODEL_DIR / "pcos_enhanced_model.joblib"

if not screening_path.exists() or not enhanced_path.exists():
    raise FileNotFoundError("Run notebooks 02 and 03 before this notebook.")

screening_artifact = joblib.load(screening_path)
enhanced_artifact = joblib.load(enhanced_path)

print("Screening model:", screening_artifact["model_name"], "threshold:", screening_artifact["threshold"])
print("Enhanced model:", enhanced_artifact["model_name"], "threshold:", enhanced_artifact["threshold"])
`),
  md(`## Global Feature Drivers`),
  code(String.raw`
def extract_feature_importance(artifact):
    model = artifact["model"]
    features = artifact["features"]
    estimator = model.named_steps["model"]

    if hasattr(estimator, "feature_importances_"):
        values = estimator.feature_importances_
        kind = "tree_importance"
    elif hasattr(estimator, "coef_"):
        values = estimator.coef_[0]
        kind = "standardized_log_odds_coefficient"
    else:
        return pd.DataFrame({"feature": features, "importance": np.nan, "kind": "not_available"})

    table = pd.DataFrame({
        "feature": features,
        "importance": values,
        "abs_importance": np.abs(values),
        "kind": kind,
    }).sort_values("abs_importance", ascending=False)
    return table

screening_importance = extract_feature_importance(screening_artifact)
enhanced_importance = extract_feature_importance(enhanced_artifact)

screening_importance.to_csv(METRIC_DIR / "screening_feature_importance.csv", index=False)
enhanced_importance.to_csv(METRIC_DIR / "enhanced_feature_importance.csv", index=False)

display(screening_importance.head(15))
display(enhanced_importance.head(20))
`),
  md(`## Plot Feature Drivers`),
  code(String.raw`
def plot_importance(table, title, path, n=15):
    plot_data = table.head(n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(plot_data["feature"], plot_data["importance"])
    ax.set_title(title)
    ax.set_xlabel("Importance")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.show()

plot_importance(
    screening_importance,
    "Top screening model drivers",
    FIGURE_DIR / "screening_feature_importance.png",
    n=15,
)

plot_importance(
    enhanced_importance,
    "Top enhanced model drivers",
    FIGURE_DIR / "enhanced_feature_importance.png",
    n=20,
)
`),
  md(`## Hold-out Demo Cases

Reproduce the test split with the same seed so demo cases come from rows the models never saw during training.`),
  code(String.raw`
def holdout_indices(features):
    X = pcos[features].copy()
    y = pcos[TARGET].copy()
    _, X_test, _, y_test = train_test_split(
        X, y,
        test_size=0.25,
        stratify=y,
        random_state=RANDOM_STATE,
    )
    return X_test.index, y_test

enh_test_idx, enh_y_test = holdout_indices(enhanced_artifact["features"])

# enh_y_test is indexed by the test split's row labels, matching enh_test_idx.
positive_test_idx = enh_test_idx[enh_y_test.values == 1][0]
negative_test_idx = enh_test_idx[enh_y_test.values == 0][0]

positive_case = pcos.loc[positive_test_idx].to_dict()
negative_case = pcos.loc[negative_test_idx].to_dict()

print(f"Positive holdout row index: {positive_test_idx}")
print(f"Negative holdout row index: {negative_test_idx}")
`),
  md(`## Patient-Level Predictions with Threshold-Aware Risk Tiers`),
  code(String.raw`
def predict_with_artifact(row, artifact):
    features = artifact["features"]
    model = artifact["model"]
    threshold = artifact["threshold"]
    tier_fn = make_risk_tier(threshold)
    X_one = pd.DataFrame([row])[features]
    probability = float(model.predict_proba(X_one)[:, 1][0])
    return {
        "probability": probability,
        "threshold": float(threshold),
        "prediction": int(probability >= threshold),
        "risk_tier": tier_fn(probability),
    }

demo_results = {
    "known_pcos_case_screening": predict_with_artifact(positive_case, screening_artifact),
    "known_pcos_case_enhanced": predict_with_artifact(positive_case, enhanced_artifact),
    "known_non_pcos_case_screening": predict_with_artifact(negative_case, screening_artifact),
    "known_non_pcos_case_enhanced": predict_with_artifact(negative_case, enhanced_artifact),
}

save_json(demo_results, METRIC_DIR / "demo_case_predictions.json")
demo_results
`),
  md(`## SHAP-Based Per-Patient Explanations

SHAP attributes each feature's contribution to a single patient's predicted log-odds. For tree models we use \`TreeExplainer\`; for logistic regression we use \`LinearExplainer\` on the scaled feature space.`),
  code(String.raw`
import shap

def transform_through_preprocessing(model, X_row):
    """Apply every pipeline step except the final estimator."""
    X = X_row.copy()
    for _, transformer in model.steps[:-1]:
        X = transformer.transform(X)
    return X

def shap_for_artifact(artifact, row, background=None, top_n=8):
    features = artifact["features"]
    model = artifact["model"]
    estimator = model.named_steps["model"]

    X_row = pd.DataFrame([row])[features]
    X_transformed = transform_through_preprocessing(model, X_row)

    if hasattr(estimator, "feature_importances_"):
        explainer = shap.TreeExplainer(estimator)
        sv = explainer.shap_values(X_transformed)
        if isinstance(sv, list):
            values = sv[1][0] if len(sv) > 1 else sv[0][0]
        elif np.ndim(sv) == 3:
            values = sv[0, :, 1]
        else:
            values = sv[0]
    elif hasattr(estimator, "coef_"):
        if background is None:
            background = X_transformed
        explainer = shap.LinearExplainer(estimator, background)
        values = np.array(explainer.shap_values(X_transformed))[0]
    else:
        return None

    table = pd.DataFrame({
        "feature": features,
        "patient_value": X_row.iloc[0].values,
        "shap_log_odds_contribution": values,
    })
    table["abs"] = table["shap_log_odds_contribution"].abs()
    return table.sort_values("abs", ascending=False).drop(columns="abs").head(top_n).reset_index(drop=True)

# Build a small background sample on the *training* slice for linear SHAP.
def training_background(artifact, size=100):
    features = artifact["features"]
    X = pcos[features].copy()
    y = pcos[TARGET].copy()
    X_train, _, _, _ = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE,
    )
    sample = X_train.sample(min(size, len(X_train)), random_state=RANDOM_STATE)
    return transform_through_preprocessing(artifact["model"], sample)

screening_background = training_background(screening_artifact)
enhanced_background = training_background(enhanced_artifact)

print("SHAP - positive holdout case, screening model:")
screening_shap = shap_for_artifact(screening_artifact, positive_case, background=screening_background)
display(screening_shap)

print("SHAP - positive holdout case, enhanced model:")
enhanced_shap = shap_for_artifact(enhanced_artifact, positive_case, background=enhanced_background)
display(enhanced_shap)

screening_shap.to_csv(METRIC_DIR / "demo_positive_screening_shap.csv", index=False)
enhanced_shap.to_csv(METRIC_DIR / "demo_positive_enhanced_shap.csv", index=False)
`),
  md(`## SHAP Waterfall Plots`),
  code(String.raw`
def plot_shap_bars(table, title, path):
    plot_data = table.iloc[::-1]
    colors = ["#d95f59" if v > 0 else "#3a7ca5" for v in plot_data["shap_log_odds_contribution"]]
    fig, ax = plt.subplots(figsize=(8, 0.5 * len(plot_data) + 2))
    ax.barh(plot_data["feature"], plot_data["shap_log_odds_contribution"], color=colors)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_title(title)
    ax.set_xlabel("SHAP contribution (log-odds)")
    for i, (val, pv) in enumerate(zip(plot_data["shap_log_odds_contribution"], plot_data["patient_value"])):
        ax.text(val, i, f"  value={pv:g}", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.show()

plot_shap_bars(
    screening_shap,
    "Screening model SHAP for known PCOS holdout case",
    FIGURE_DIR / "screening_shap_positive_case.png",
)
plot_shap_bars(
    enhanced_shap,
    "Enhanced model SHAP for known PCOS holdout case",
    FIGURE_DIR / "enhanced_shap_positive_case.png",
)
`),
  md(`## Model Card`),
  code(String.raw`
model_card = f"""
# PCOS Pathfinder Model Card

## Intended use

Decision support for PCOS risk screening and diagnostic triage. **Not** a standalone diagnostic device.

## Data

- Required PCOS clinical dataset (10 hospitals, Kerala, India).
- Cleaned rows: {len(pcos)}
- PCOS-positive: {int(pcos[TARGET].sum())} | PCOS-negative: {int((pcos[TARGET] == 0).sum())}
- Columns dropped during cleaning: {pcos.attrs.get("dropped_columns", [])}

## Models

### Screening model

- Algorithm: {screening_artifact["model_name"]}
- Features: {len(screening_artifact["features"])} (no lifestyle proxies)
- Threshold: {screening_artifact["threshold"]:.3f} (chosen on training CV at recall>=0.90)
- Holdout ROC-AUC: {screening_artifact["metrics"].get("roc_auc"):.3f}
- Holdout recall / specificity: {screening_artifact["metrics"].get("recall"):.3f} / {screening_artifact["metrics"].get("specificity"):.3f}

### Enhanced model

- Algorithm: {enhanced_artifact["model_name"]}
- Features: {len(enhanced_artifact["features"])}
- Threshold: {enhanced_artifact["threshold"]:.3f} (chosen on training CV at recall>=0.90)
- Holdout ROC-AUC: {enhanced_artifact["metrics"].get("roc_auc"):.3f}
- Holdout recall / specificity: {enhanced_artifact["metrics"].get("recall"):.3f} / {enhanced_artifact["metrics"].get("specificity"):.3f}

## Explainability

- Global: tree feature importances or scaled logistic-regression coefficients.
- Local: SHAP attributions for each prediction.

## Limitations

- Single-source geography (Kerala, India); generalisation requires external validation.
- Small dataset ({len(pcos)} rows).
- Endometriosis overlap module uses synthetic data and only prompts further workup.
- Demographic equity variables (race, income, access to care) are not available.
- Outputs must be combined with clinical judgement.
"""

model_card_path = METRIC_DIR / "pcos_model_card.md"
model_card_path.write_text(model_card, encoding="utf-8")
print("Saved:", model_card_path)
print(model_card)
`),
]);

const notebook06 = nb([
  md(`# 06 - Single-Cell Gene Peek (Biological Rationale)

Purpose:

- Open the supplementary PCOS single-cell archive without performing a full single-cell analysis.
- Extract gene symbols from one sample's \`features.tsv.gz\`.
- Cross-reference with a small list of literature-supported PCOS genes.
- Produce a small CSV that the deck can cite as biological rationale.

This is intentionally a peek, not a single-cell expression analysis. We are not running QC, normalisation, or DE here.`),
  code(String.raw`
from pathlib import Path
import io
import gzip
import tarfile
import zipfile

import numpy as np
import pandas as pd

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
RAW_DIR = PROJECT_ROOT / "_read_extract"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
METRIC_DIR = OUTPUT_DIR / "metrics"

PCOS_SC_ZIP = RAW_DIR / "(Supplementary_Dataset)_PCOS_single_cell_data.zip"
ENDO_SC_ZIP = RAW_DIR / "(Supplementary_Dataset)_Endometrium_single_cell_data.zip"

# Curated list of PCOS-associated genes (illustrative, from published GWAS and biology reviews).
PCOS_LITERATURE_GENES = {
    "CYP17A1": "Steroidogenesis; ovarian androgen production",
    "CYP19A1": "Aromatase; androgen-to-estrogen conversion",
    "AMH": "Anti-Mullerian Hormone; elevated in PCOS follicles",
    "AMHR2": "AMH receptor; granulosa cell signalling",
    "AR": "Androgen receptor; hyperandrogenism phenotype",
    "INSR": "Insulin receptor; insulin resistance in PCOS",
    "DENND1A": "PCOS susceptibility locus (GWAS)",
    "FSHR": "FSH receptor; follicular development",
    "LHCGR": "LH/CG receptor; ovarian theca signalling",
    "THADA": "PCOS susceptibility locus (GWAS)",
    "FSHB": "FSH beta subunit; PCOS GWAS",
    "GATA4": "Granulosa cell transcription factor",
    "STAR": "Steroidogenic Acute Regulatory protein",
    "HSD17B3": "Androgen biosynthesis",
    "HSD3B2": "Steroid biosynthesis",
    "SRD5A1": "5-alpha reductase; androgen amplification",
    "SRD5A2": "5-alpha reductase; androgen amplification",
    "INS": "Insulin gene",
    "IRS1": "Insulin receptor substrate 1",
    "IRS2": "Insulin receptor substrate 2",
}
`),
  md(`## Peek at One Sample's Gene List`),
  code(String.raw`
TAR_SUFFIXES = (".tar.gz", ".tgz", ".tar")

def _strip_tar_suffix(name):
    for suf in TAR_SUFFIXES:
        if name.endswith(suf):
            return name[: -len(suf)]
    return name

def first_features_table(zip_path):
    """Return (sample_name, gene_table) for the first features.tsv.gz inside the first inner tar."""
    if not zip_path.exists():
        return None, None
    with zipfile.ZipFile(zip_path) as zf:
        tar_members = [n for n in zf.namelist() if n.endswith(TAR_SUFFIXES)]
        if not tar_members:
            return None, None
        member = sorted(tar_members)[0]
        sample_name = _strip_tar_suffix(Path(member).name)
        tar_bytes = zf.read(member)
    # tarfile.open auto-detects gzip-compressed tars when given a file-like object.
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tar:
        for m in tar.getmembers():
            if m.name.endswith("features.tsv.gz"):
                fh = tar.extractfile(m)
                if fh is None:
                    continue
                with gzip.open(fh, "rt") as gz:
                    df = pd.read_csv(
                        gz, sep="\t", header=None,
                        names=["ensembl_id", "gene_symbol", "feature_type"],
                    )
                return sample_name, df
    return sample_name, None

sample_name, genes_df = first_features_table(PCOS_SC_ZIP)

if genes_df is None:
    print("Skipping: PCOS single-cell archive not present at", PCOS_SC_ZIP)
else:
    print(f"Sample peeked: {sample_name}")
    print(f"Total features in this sample: {len(genes_df):,}")
    display(genes_df.head())
`),
  md(`## Match Against Literature-Supported PCOS Genes`),
  code(String.raw`
if genes_df is not None:
    found = genes_df[genes_df["gene_symbol"].isin(PCOS_LITERATURE_GENES.keys())].copy()
    found["literature_context"] = found["gene_symbol"].map(PCOS_LITERATURE_GENES)
    found = found.drop_duplicates(subset=["gene_symbol"]).reset_index(drop=True)
    found.to_csv(METRIC_DIR / "single_cell_pcos_gene_overlap.csv", index=False)
    print(f"Literature-supported PCOS genes present in sample ({len(found)} of {len(PCOS_LITERATURE_GENES)}):")
    display(found)
else:
    print("No gene list to match.")
`),
  md(`## Sample Inventory Across Both Archives`),
  code(String.raw`
def list_samples(zip_path):
    if not zip_path.exists():
        return []
    with zipfile.ZipFile(zip_path) as zf:
        return sorted({_strip_tar_suffix(Path(n).name) for n in zf.namelist() if n.endswith(TAR_SUFFIXES)})

pcos_samples = list_samples(PCOS_SC_ZIP)
endo_samples = list_samples(ENDO_SC_ZIP)

inventory = pd.DataFrame({
    "archive": (["pcos_single_cell"] * len(pcos_samples)) + (["endometrium_single_cell"] * len(endo_samples)),
    "sample": pcos_samples + endo_samples,
})
inventory.to_csv(METRIC_DIR / "single_cell_sample_inventory.csv", index=False)
print(f"PCOS samples: {len(pcos_samples)} | Endometrium samples: {len(endo_samples)}")
inventory
`),
  md(`## Slide-Ready Takeaway

> The provided PCOS single-cell archive contains [N] samples covering known PCOS biology, including steroidogenesis (CYP17A1, CYP19A1), insulin signalling (INSR, IRS1/2), and PCOS GWAS hits (DENND1A, THADA, FSHB). These genes appear in the per-sample feature lists, giving us a defensible biological rationale for the clinical features we model (hyperandrogenism, insulin resistance, follicular dysfunction). Full single-cell DE analysis is left as future work.`),
]);

const readme = `# Training Notebooks

Run order:

1. \`01_pcos_data_audit_and_eda.ipynb\` - load, clean, audit, save processed CSV.
2. \`02_train_pcos_screening_model.ipynb\` - low-cost primary-care screening model.
3. \`03_train_pcos_enhanced_model.ipynb\` - diagnostic-support model with labs and ultrasound.
4. \`04_train_endometriosis_overlap_model.ipynb\` - differential-diagnosis prompt (synthetic data).
5. \`05_thresholds_explainability_and_demo.ipynb\` - SHAP, holdout demo cases, model card.
6. \`06_single_cell_gene_peek.ipynb\` - optional biological rationale slide.

Outputs land in:

- \`outputs/figures/\` - plots used in the deck.
- \`outputs/metrics/\` - CSV and JSON metric exports.
- \`outputs/models/\` - joblib model artifacts.

They expect either the extracted files in \`_read_extract/\` or the original \`OneDrive_1_5-11-2026.zip\` in the project root.

Install dependencies with:

\`\`\`bash
pip install -r requirements.txt
\`\`\`
`;

const requirements = `# Pinned to the versions used when training the artifacts under outputs/models/.
# joblib model artifacts are sensitive to scikit-learn major versions, so the
# pins are tight rather than open ranges.
pandas==2.2.3
numpy==2.2.6
scikit-learn==1.6.1
matplotlib==3.10.1
seaborn==0.13.2
openpyxl==3.1.5
joblib==1.4.2
shap==0.51.0
streamlit==1.32.0
jupyter==1.0.0
nbconvert==7.17.0
reportlab==4.4.9
pillow==10.3.0
pypdf==4.0.0
`;

const files = [
  ["01_pcos_data_audit_and_eda.ipynb", notebook01],
  ["02_train_pcos_screening_model.ipynb", notebook02],
  ["03_train_pcos_enhanced_model.ipynb", notebook03],
  ["04_train_endometriosis_overlap_model.ipynb", notebook04],
  ["05_thresholds_explainability_and_demo.ipynb", notebook05],
  ["06_single_cell_gene_peek.ipynb", notebook06],
];

for (const [name, notebook] of files) {
  fs.writeFileSync(path.join(notebooksDir, name), JSON.stringify(notebook, null, 2), "utf8");
}

fs.writeFileSync(path.join(notebooksDir, "README.md"), readme, "utf8");
fs.writeFileSync(path.join(root, "requirements.txt"), requirements, "utf8");

console.log(`Wrote ${files.length} notebooks to ${notebooksDir}`);
