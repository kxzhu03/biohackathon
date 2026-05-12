"""Build notebooks/10_tabpfn_benchmark.ipynb with nbformat.

Run from project root: python scripts/build_notebook_10.py
"""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parent.parent
NB_PATH = ROOT / "notebooks" / "10_tabpfn_benchmark.ipynb"

nb = nbf.v4.new_notebook()
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.12",
    },
}

cells = []

cells.append(nbf.v4.new_markdown_cell(
    "# 10 - TabPFN-v2 Benchmark vs. Random Forest\n\n"
    "Benchmarks **TabPFN-v2** (Hollmann et al., *Nature* 2025) against the saved "
    "random-forest screening and enhanced PCOS models.\n\n"
    "TabPFN-v2 is a transformer foundation model pre-trained on synthetic tabular tasks. "
    "The paper reports it beats gradient-boosted trees on small tabular problems (n < 10,000). "
    "Our PCOS cohort (n = 541) is squarely in that regime, so this benchmark is a strong "
    "innovation signal.\n\n"
    "**Robustness:** if `tabpfn` cannot install or load (e.g. the prior-checkpoint download fails "
    "in a sandboxed environment), the notebook still executes and emits a JSON stub explaining "
    "the failure, so downstream integration steps never break.\n\n"
    "**Reproducibility:** uses the same `train_test_split(test_size=0.25, stratify=y, "
    "random_state=42)` as notebooks 02 and 03, and the same high-recall thresholds saved in the "
    "model artifacts."
))

cells.append(nbf.v4.new_code_cell(
    "# Install / upgrade TabPFN. Safe to re-run.\n"
    "# We pin to a 6.x release of TabPFN-v2 (Hollmann et al., Nature 2025): from\n"
    "# 7.x onwards Prior Labs moved the model weights behind a one-time license gate\n"
    "# that needs an interactive browser flow (sets TABPFN_TOKEN), which would force\n"
    "# this notebook to skip in CI / sandboxed runs. The 2.x-6.x series ships open\n"
    "# weights and is the same TabPFN-v2 architecture/checkpoint.\n"
    "# Use sys.executable -m pip (instead of bare `!pip ...`) so shell quoting of\n"
    "# `<` is bypassed by argv handling.\n"
    "import sys, subprocess\n"
    "subprocess.run(\n"
    "    [sys.executable, '-m', 'pip', 'install', '--upgrade', '--quiet', 'tabpfn<7'],\n"
    "    check=False,\n"
    ")"
))

cells.append(nbf.v4.new_code_cell(
    "from pathlib import Path\n"
    "import json\n"
    "import time\n"
    "import warnings\n"
    "\n"
    "import joblib\n"
    "import numpy as np\n"
    "import pandas as pd\n"
    "import matplotlib.pyplot as plt\n"
    "import seaborn as sns\n"
    "\n"
    "from sklearn.impute import SimpleImputer\n"
    "from sklearn.metrics import (\n"
    "    fbeta_score,\n"
    "    f1_score,\n"
    "    recall_score,\n"
    "    roc_auc_score,\n"
    ")\n"
    "from sklearn.model_selection import train_test_split\n"
    "\n"
    "warnings.filterwarnings('ignore')\n"
    "sns.set_theme(style='whitegrid')\n"
    "plt.rcParams['figure.dpi'] = 110\n"
    "\n"
    "RANDOM_STATE = 42\n"
    "TEST_SIZE = 0.25\n"
    "\n"
    "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
    "DATA_PATH = PROJECT_ROOT / 'outputs' / 'pcos_cleaned.csv'\n"
    "MODEL_DIR = PROJECT_ROOT / 'outputs' / 'models'\n"
    "METRIC_DIR = PROJECT_ROOT / 'outputs' / 'metrics'\n"
    "FIGURE_DIR = PROJECT_ROOT / 'outputs' / 'figures'\n"
    "for folder in (METRIC_DIR, FIGURE_DIR):\n"
    "    folder.mkdir(parents=True, exist_ok=True)\n"
    "\n"
    "COMPARISON_PATH = METRIC_DIR / 'tabpfn_comparison.json'\n"
    "FIGURE_PATH = FIGURE_DIR / 'tabpfn_vs_rf_auc.png'\n"
    "\n"
    "print('Project root:', PROJECT_ROOT)\n"
    "print('Data path:', DATA_PATH, '(exists:', DATA_PATH.exists(), ')')"
))

cells.append(nbf.v4.new_markdown_cell(
    "## Try importing TabPFN\n\n"
    "If the import fails for any reason (no network access to fetch the prior checkpoint, "
    "missing torch CUDA build, etc.), we write a `skipped` stub and exit gracefully so "
    "integration code can still rely on the file existing."
))

cells.append(nbf.v4.new_code_cell(
    "tabpfn_ok = False\n"
    "tabpfn_error = None\n"
    "tabpfn_version = None\n"
    "TabPFNClassifier = None\n"
    "\n"
    "try:\n"
    "    import tabpfn\n"
    "    from tabpfn import TabPFNClassifier as _TabPFNClassifier\n"
    "    tabpfn_version = getattr(tabpfn, '__version__', 'unknown')\n"
    "    TabPFNClassifier = _TabPFNClassifier\n"
    "    tabpfn_ok = True\n"
    "    print('TabPFN imported. Version:', tabpfn_version)\n"
    "except Exception as exc:\n"
    "    tabpfn_error = f'{type(exc).__name__}: {exc}'\n"
    "    print('TabPFN import failed:', tabpfn_error)\n"
    "\n"
    "# Pick device. TabPFN-v2 runs comfortably on CPU for n < 10k.\n"
    "device = 'cpu'\n"
    "try:\n"
    "    import torch\n"
    "    if torch.cuda.is_available():\n"
    "        device = 'cuda'\n"
    "except Exception:\n"
    "    pass\n"
    "print('Selected device:', device)"
))

cells.append(nbf.v4.new_markdown_cell(
    "## Helpers"
))

cells.append(nbf.v4.new_code_cell(
    "def write_skip_stub(reason, comparison_path=COMPARISON_PATH):\n"
    "    payload = {\n"
    "        'status': 'skipped',\n"
    "        'reason': str(reason),\n"
    "        'fallback': 'random_forest',\n"
    "    }\n"
    "    comparison_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')\n"
    "    print('Wrote skip stub to', comparison_path)\n"
    "    return payload\n"
    "\n"
    "\n"
    "def metric_block(y_true, y_proba, threshold, fit_seconds, predict_seconds):\n"
    "    y_pred = (y_proba >= threshold).astype(int)\n"
    "    return {\n"
    "        'threshold': float(threshold),\n"
    "        'roc_auc': float(roc_auc_score(y_true, y_proba)),\n"
    "        'recall': float(recall_score(y_true, y_pred)),\n"
    "        'specificity': float(recall_score(y_true, y_pred, pos_label=0)),\n"
    "        'f1': float(f1_score(y_true, y_pred)),\n"
    "        'f2': float(fbeta_score(y_true, y_pred, beta=2.0)),\n"
    "        'fit_seconds': None if fit_seconds is None else float(fit_seconds),\n"
    "        'predict_seconds': float(predict_seconds),\n"
    "    }\n"
    "\n"
    "\n"
    "def evaluate_rf_artifact(artifact, X_test, y_test):\n"
    "    # The saved pipeline includes its own imputer; predict_proba on the raw frame.\n"
    "    rf_pipe = artifact['model']\n"
    "    threshold = float(artifact['threshold'])\n"
    "    t0 = time.perf_counter()\n"
    "    rf_proba = rf_pipe.predict_proba(X_test)[:, 1]\n"
    "    predict_seconds = time.perf_counter() - t0\n"
    "    return metric_block(\n"
    "        y_test, rf_proba, threshold,\n"
    "        fit_seconds=None,  # RF is loaded pre-fit from joblib; no comparable fit time.\n"
    "        predict_seconds=predict_seconds,\n"
    "    )\n"
    "\n"
    "\n"
    "def fit_predict_tabpfn(X_train, y_train, X_test, device='cpu'):\n"
    "    # TabPFN does not impute internally; mirror the RF pipeline's median imputer.\n"
    "    imputer = SimpleImputer(strategy='median')\n"
    "    X_train_imp = imputer.fit_transform(X_train)\n"
    "    X_test_imp = imputer.transform(X_test)\n"
    "    try:\n"
    "        clf = TabPFNClassifier(device=device, random_state=RANDOM_STATE)\n"
    "    except TypeError:\n"
    "        # Older API may not accept device/random_state kwargs.\n"
    "        clf = TabPFNClassifier()\n"
    "    t0 = time.perf_counter()\n"
    "    clf.fit(X_train_imp, np.asarray(y_train))\n"
    "    fit_seconds = time.perf_counter() - t0\n"
    "    t1 = time.perf_counter()\n"
    "    proba = clf.predict_proba(X_test_imp)[:, 1]\n"
    "    predict_seconds = time.perf_counter() - t1\n"
    "    return proba, fit_seconds, predict_seconds"
))

cells.append(nbf.v4.new_markdown_cell(
    "## Load cleaned data and saved artifacts"
))

cells.append(nbf.v4.new_code_cell(
    "pcos = pd.read_csv(DATA_PATH)\n"
    "TARGET = 'pcos_y_n'\n"
    "print('PCOS shape:', pcos.shape)\n"
    "print(pcos[TARGET].value_counts().sort_index())\n"
    "\n"
    "screening_artifact = joblib.load(MODEL_DIR / 'pcos_screening_model.joblib')\n"
    "enhanced_artifact = joblib.load(MODEL_DIR / 'pcos_enhanced_model.joblib')\n"
    "\n"
    "MODEL_SPECS = {\n"
    "    'screening': screening_artifact,\n"
    "    'enhanced': enhanced_artifact,\n"
    "}\n"
    "for name, art in MODEL_SPECS.items():\n"
    "    print(f'\\n[{name}] features ({len(art[\"features\"])}), threshold={art[\"threshold\"]}, model_name={art.get(\"model_name\")}')"
))

cells.append(nbf.v4.new_markdown_cell(
    "## Run the benchmark\n\n"
    "Wrap the actual TabPFN call in `try/except`. On any failure we still write the JSON stub "
    "so downstream code never sees a missing file."
))

cells.append(nbf.v4.new_code_cell(
    "comparison = {\n"
    "    'screening': {},\n"
    "    'enhanced': {},\n"
    "    'device': device,\n"
    "    'tabpfn_version': tabpfn_version,\n"
    "    'notes': 'TabPFN-v2 = Hollmann et al., Nature 2025',\n"
    "}\n"
    "\n"
    "if not tabpfn_ok:\n"
    "    write_skip_stub(tabpfn_error or 'TabPFN import failed')\n"
    "else:\n"
    "    try:\n"
    "        for spec_name, artifact in MODEL_SPECS.items():\n"
    "            features = artifact['features']\n"
    "            threshold = float(artifact['threshold'])\n"
    "            X = pcos[features].copy()\n"
    "            y = pcos[TARGET].astype(int).copy()\n"
    "\n"
    "            X_train, X_test, y_train, y_test = train_test_split(\n"
    "                X, y,\n"
    "                test_size=TEST_SIZE,\n"
    "                stratify=y,\n"
    "                random_state=RANDOM_STATE,\n"
    "            )\n"
    "\n"
    "            # --- TabPFN ---\n"
    "            print(f'\\n[{spec_name}] fitting TabPFN on {X_train.shape[0]} rows x {X_train.shape[1]} features ...')\n"
    "            tab_proba, tab_fit_s, tab_pred_s = fit_predict_tabpfn(\n"
    "                X_train, y_train, X_test, device=device,\n"
    "            )\n"
    "            tabpfn_metrics = metric_block(y_test, tab_proba, threshold, tab_fit_s, tab_pred_s)\n"
    "            print(f'  fit={tab_fit_s:.2f}s, predict={tab_pred_s:.2f}s, '\n"
    "                  f'roc_auc={tabpfn_metrics[\"roc_auc\"]:.3f}, recall={tabpfn_metrics[\"recall\"]:.3f}')\n"
    "\n"
    "            # --- Random forest (saved artifact, already fit) ---\n"
    "            rf_metrics = evaluate_rf_artifact(artifact, X_test, y_test)\n"
    "            print(f'  RF  fit=cached, predict={rf_metrics[\"predict_seconds\"]:.3f}s, '\n"
    "                  f'roc_auc={rf_metrics[\"roc_auc\"]:.3f}, recall={rf_metrics[\"recall\"]:.3f}')\n"
    "\n"
    "            comparison[spec_name] = {\n"
    "                'tabpfn': tabpfn_metrics,\n"
    "                'random_forest': rf_metrics,\n"
    "                'n_train': int(X_train.shape[0]),\n"
    "                'n_test': int(X_test.shape[0]),\n"
    "                'n_features': int(X_train.shape[1]),\n"
    "            }\n"
    "\n"
    "        comparison['status'] = 'ok'\n"
    "        COMPARISON_PATH.write_text(json.dumps(comparison, indent=2), encoding='utf-8')\n"
    "        print('\\nWrote comparison to', COMPARISON_PATH)\n"
    "    except Exception as exc:\n"
    "        msg = f'{type(exc).__name__}: {exc}'\n"
    "        print('TabPFN training failed:', msg)\n"
    "        write_skip_stub(msg)"
))

cells.append(nbf.v4.new_markdown_cell(
    "## Plot ROC-AUC comparison\n\n"
    "Only drawn when we have real numbers; otherwise we skip the figure."
))

cells.append(nbf.v4.new_code_cell(
    "payload = json.loads(COMPARISON_PATH.read_text(encoding='utf-8'))\n"
    "\n"
    "if payload.get('status') == 'ok':\n"
    "    rows = []\n"
    "    for spec in ('screening', 'enhanced'):\n"
    "        rows.append({'feature_set': spec, 'model': 'TabPFN-v2', 'roc_auc': payload[spec]['tabpfn']['roc_auc']})\n"
    "        rows.append({'feature_set': spec, 'model': 'Random Forest', 'roc_auc': payload[spec]['random_forest']['roc_auc']})\n"
    "    plot_df = pd.DataFrame(rows)\n"
    "\n"
    "    fig, ax = plt.subplots(figsize=(6, 4))\n"
    "    sns.barplot(\n"
    "        data=plot_df,\n"
    "        x='feature_set', y='roc_auc', hue='model',\n"
    "        palette={'TabPFN-v2': '#4c72b0', 'Random Forest': '#dd8452'},\n"
    "        ax=ax,\n"
    "    )\n"
    "    ax.set_ylim(0.5, 1.0)\n"
    "    ax.set_ylabel('ROC-AUC (held-out test, n=136)')\n"
    "    ax.set_xlabel('Feature set')\n"
    "    ax.set_title('TabPFN-v2 vs. Random Forest on PCOS (n=541)')\n"
    "    for container in ax.containers:\n"
    "        ax.bar_label(container, fmt='%.3f', padding=2)\n"
    "    ax.legend(loc='lower right')\n"
    "    fig.tight_layout()\n"
    "    fig.savefig(FIGURE_PATH, dpi=160)\n"
    "    plt.show()\n"
    "    print('Saved figure to', FIGURE_PATH)\n"
    "else:\n"
    "    print('Skipped figure: status =', payload.get('status'), '-', payload.get('reason'))"
))

cells.append(nbf.v4.new_markdown_cell(
    "## Side-by-side summary table"
))

cells.append(nbf.v4.new_code_cell(
    "if payload.get('status') == 'ok':\n"
    "    rows = []\n"
    "    for spec in ('screening', 'enhanced'):\n"
    "        for model_name in ('tabpfn', 'random_forest'):\n"
    "            block = payload[spec][model_name]\n"
    "            rows.append({\n"
    "                'feature_set': spec,\n"
    "                'model': model_name,\n"
    "                'roc_auc': round(block['roc_auc'], 4),\n"
    "                'recall': round(block['recall'], 4),\n"
    "                'specificity': round(block['specificity'], 4),\n"
    "                'f1': round(block['f1'], 4),\n"
    "                'f2': round(block['f2'], 4),\n"
    "                'fit_s': round(block['fit_seconds'], 3) if block.get('fit_seconds') is not None else None,\n"
    "                'predict_s': round(block['predict_seconds'], 4),\n"
    "            })\n"
    "    summary = pd.DataFrame(rows)\n"
    "    display(summary)\n"
    "else:\n"
    "    print('Skipped summary: status =', payload.get('status'))"
))

cells.append(nbf.v4.new_markdown_cell(
    "## Output file assertion\n\n"
    "Final guardrail so the integration step never trips on a missing or empty file."
))

cells.append(nbf.v4.new_code_cell(
    "assert COMPARISON_PATH.exists(), f'Missing output: {COMPARISON_PATH}'\n"
    "assert COMPARISON_PATH.stat().st_size > 0, f'Empty output: {COMPARISON_PATH}'\n"
    "print('OK:', COMPARISON_PATH, '(', COMPARISON_PATH.stat().st_size, 'bytes )')"
))

nb["cells"] = cells

NB_PATH.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, str(NB_PATH))
print('Wrote', NB_PATH)
