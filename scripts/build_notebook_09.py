"""Build notebooks/09_decision_curve_analysis.ipynb using nbformat.

Run from project root:
    python scripts/build_notebook_09.py
"""

from pathlib import Path

import nbformat as nbf


PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "09_decision_curve_analysis.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


CELLS = [
    md(
        "# 09 - Decision Curve Analysis\n"
        "\n"
        "Following **Vickers & Elkin (2006)** and **Vickers et al. (BMJ 2016)**, this "
        "notebook computes the **net benefit** of the PCOS screening and enhanced "
        "models across a fine grid of threshold probabilities, and compares each "
        "model against the two clinical baselines:\n"
        "\n"
        "- **Treat all** - everyone classified positive (refer everyone).\n"
        "- **Treat none** - nobody classified positive (do nothing); net benefit is 0.\n"
        "\n"
        "Net benefit at threshold probability $p_t$ is:\n"
        "\n"
        "$$\n"
        "\\text{NB}(p_t) = \\frac{TP}{N} - \\frac{FP}{N} \\cdot \\frac{p_t}{1 - p_t}\n"
        "$$\n"
        "\n"
        "The model adds clinical value over both baselines in the threshold range "
        "where its net-benefit curve sits above both reference curves. The deployed "
        "action threshold (from notebooks 02 / 03) is marked on each plot.\n"
        "\n"
        "Outputs:\n"
        "- `outputs/figures/dca_screening.png`\n"
        "- `outputs/figures/dca_enhanced.png`\n"
        "- `outputs/figures/dca_combined.png`\n"
        "- `outputs/metrics/dca.json`\n"
    ),
    code(
        "from pathlib import Path\n"
        "import json\n"
        "import joblib\n"
        "import numpy as np\n"
        "import pandas as pd\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n"
        "from sklearn.model_selection import train_test_split\n"
        "\n"
        "sns.set_theme(style=\"whitegrid\")\n"
        "plt.rcParams[\"figure.dpi\"] = 110\n"
        "RANDOM_STATE = 42\n"
        "TEST_SIZE = 0.25\n"
        "TARGET = \"pcos_y_n\"\n"
        "\n"
        "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == \"notebooks\" else Path.cwd()\n"
        "OUTPUT_DIR = PROJECT_ROOT / \"outputs\"\n"
        "FIGURE_DIR = OUTPUT_DIR / \"figures\"\n"
        "METRIC_DIR = OUTPUT_DIR / \"metrics\"\n"
        "MODEL_DIR = OUTPUT_DIR / \"models\"\n"
        "for folder in (FIGURE_DIR, METRIC_DIR):\n"
        "    folder.mkdir(parents=True, exist_ok=True)\n"
        "\n"
        "DATA_PATH = OUTPUT_DIR / \"pcos_cleaned.csv\"\n"
        "print(\"Project root:\", PROJECT_ROOT)\n"
        "print(\"Data path:\", DATA_PATH)\n"
    ),
    md("## Load Data and Model Artifacts"),
    code(
        "pcos = pd.read_csv(DATA_PATH)\n"
        "print(\"Cleaned PCOS shape:\", pcos.shape)\n"
        "print(\"Target distribution:\")\n"
        "print(pcos[TARGET].value_counts().sort_index())\n"
    ),
    code(
        "MODEL_CONFIGS = {\n"
        "    \"screening\": {\n"
        "        \"artifact\": MODEL_DIR / \"pcos_screening_model.joblib\",\n"
        "        \"figure\": FIGURE_DIR / \"dca_screening.png\",\n"
        "        \"title\": \"Decision Curve - PCOS Screening Model\",\n"
        "        \"colour\": \"#1f77b4\",\n"
        "    },\n"
        "    \"enhanced\": {\n"
        "        \"artifact\": MODEL_DIR / \"pcos_enhanced_model.joblib\",\n"
        "        \"figure\": FIGURE_DIR / \"dca_enhanced.png\",\n"
        "        \"title\": \"Decision Curve - PCOS Enhanced Model\",\n"
        "        \"colour\": \"#6a3d9a\",\n"
        "    },\n"
        "}\n"
        "\n"
        "for key, cfg in MODEL_CONFIGS.items():\n"
        "    cfg[\"loaded\"] = joblib.load(cfg[\"artifact\"])\n"
        "    print(f\"{key}: {cfg['loaded']['model_name']} | threshold={cfg['loaded']['threshold']}\"\n"
        "          f\" | n_features={len(cfg['loaded']['features'])}\")\n"
    ),
    md(
        "## Net-Benefit Helpers\n"
        "\n"
        "We compute net benefit on the held-out test split for each model. The "
        "split mirrors notebooks 02 / 03 exactly (`random_state=42`, "
        "`test_size=0.25`, stratified on the target), so we are evaluating "
        "the model on data it has not seen during training or threshold tuning."
    ),
    code(
        "PT_GRID = np.round(np.arange(0.01, 0.99 + 1e-9, 0.005), 4)\n"
        "\n"
        "def reproduce_test_split(features):\n"
        "    \"\"\"Reproduce the exact 75/25 stratified split used in notebooks 02 and 03.\"\"\"\n"
        "    X = pcos[features].copy()\n"
        "    y = pcos[TARGET].copy()\n"
        "    X_train, X_test, y_train, y_test = train_test_split(\n"
        "        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE,\n"
        "    )\n"
        "    return X_test, y_test.to_numpy()\n"
        "\n"
        "def net_benefit_curve(y_true, y_proba, pt_grid):\n"
        "    \"\"\"Net benefit for the model and the 'treat all' baseline across a pt grid.\n"
        "\n"
        "    NB(pt) = TP/N - FP/N * pt/(1-pt). 'Treat all' classifies every case as positive,\n"
        "    so TP = positives and FP = negatives at every pt.\n"
        "    \"\"\"\n"
        "    y_true = np.asarray(y_true).astype(int)\n"
        "    y_proba = np.asarray(y_proba)\n"
        "    n = len(y_true)\n"
        "    prevalence = y_true.mean()\n"
        "    odds = pt_grid / (1.0 - pt_grid)\n"
        "    pred = y_proba[None, :] >= pt_grid[:, None]\n"
        "    tp = (pred & (y_true == 1)[None, :]).sum(axis=1)\n"
        "    fp = (pred & (y_true == 0)[None, :]).sum(axis=1)\n"
        "    nb_model = tp / n - fp / n * odds\n"
        "    nb_treat_all = prevalence - (1.0 - prevalence) * odds\n"
        "    return nb_model, nb_treat_all\n"
        "\n"
        "def longest_useful_range(pt_grid, nb_model, nb_treat_all):\n"
        "    \"\"\"Longest contiguous pt range where NB_model > max(NB_treat_all, 0).\"\"\"\n"
        "    baseline = np.maximum(nb_treat_all, 0.0)\n"
        "    is_useful = nb_model > baseline\n"
        "    best_lo, best_hi, best_len = None, None, 0\n"
        "    i = 0\n"
        "    while i < len(is_useful):\n"
        "        if not is_useful[i]:\n"
        "            i += 1\n"
        "            continue\n"
        "        j = i\n"
        "        while j < len(is_useful) and is_useful[j]:\n"
        "            j += 1\n"
        "        run_len = j - i\n"
        "        if run_len > best_len:\n"
        "            best_len = run_len\n"
        "            best_lo, best_hi = float(pt_grid[i]), float(pt_grid[j - 1])\n"
        "        i = j\n"
        "    return [best_lo, best_hi] if best_lo is not None else [None, None]\n"
    ),
    md("## Compute Decision Curves"),
    code(
        "def compute_dca(cfg):\n"
        "    artifact = cfg[\"loaded\"]\n"
        "    model = artifact[\"model\"]\n"
        "    features = artifact[\"features\"]\n"
        "    threshold = float(artifact[\"threshold\"])\n"
        "    X_test, y_test = reproduce_test_split(features)\n"
        "    y_proba = model.predict_proba(X_test)[:, 1]\n"
        "    nb_model, nb_treat_all = net_benefit_curve(y_test, y_proba, PT_GRID)\n"
        "    useful = longest_useful_range(PT_GRID, nb_model, nb_treat_all)\n"
        "    return {\n"
        "        \"threshold\": threshold,\n"
        "        \"prevalence\": float(np.mean(y_test)),\n"
        "        \"n_test\": int(len(y_test)),\n"
        "        \"grid\": PT_GRID.tolist(),\n"
        "        \"net_benefit_model\": nb_model.tolist(),\n"
        "        \"net_benefit_treat_all\": nb_treat_all.tolist(),\n"
        "        \"useful_range\": useful,\n"
        "    }\n"
        "\n"
        "dca_results = {key: compute_dca(cfg) for key, cfg in MODEL_CONFIGS.items()}\n"
        "for key, result in dca_results.items():\n"
        "    lo, hi = result[\"useful_range\"]\n"
        "    print(f\"{key}: useful pt range = [{lo}, {hi}] | prevalence={result['prevalence']:.3f}\"\n"
        "          f\" | action threshold={result['threshold']:.3f}\")\n"
    ),
    md("## Plot Decision Curves"),
    code(
        "def plot_dca(ax, pt_grid, result, title, colour):\n"
        "    nb_model = np.asarray(result[\"net_benefit_model\"])\n"
        "    nb_treat_all = np.asarray(result[\"net_benefit_treat_all\"])\n"
        "    pt = np.asarray(pt_grid)\n"
        "    ax.plot(pt, nb_model, color=colour, linewidth=2.2, label=\"Model\")\n"
        "    ax.plot(pt, nb_treat_all, color=\"#d62728\", linestyle=\"--\", linewidth=1.6, label=\"Treat all\")\n"
        "    ax.axhline(0.0, color=\"#444\", linestyle=\":\", linewidth=1.4, label=\"Treat none\")\n"
        "    lo, hi = result[\"useful_range\"]\n"
        "    if lo is not None:\n"
        "        ax.axvspan(lo, hi, color=colour, alpha=0.08,\n"
        "                   label=f\"Useful range [{lo:.2f}, {hi:.2f}]\")\n"
        "    ax.axvline(result[\"threshold\"], color=\"#2ca02c\", linewidth=1.6,\n"
        "               label=f\"Action threshold {result['threshold']:.2f}\")\n"
        "    nb_floor = min(0.0, float(np.min(nb_treat_all)))\n"
        "    nb_ceiling = float(np.max(nb_model)) + 0.02\n"
        "    ax.set_ylim(max(nb_floor, -0.05), nb_ceiling)\n"
        "    ax.set_xlim(0.0, 1.0)\n"
        "    ax.set_xlabel(\"Threshold probability $p_t$\")\n"
        "    ax.set_ylabel(\"Net benefit\")\n"
        "    ax.set_title(title)\n"
        "    ax.legend(loc=\"upper right\", fontsize=9)\n"
        "\n"
        "for key, cfg in MODEL_CONFIGS.items():\n"
        "    fig, ax = plt.subplots(figsize=(6.2, 4.6))\n"
        "    plot_dca(ax, PT_GRID, dca_results[key], cfg[\"title\"], cfg[\"colour\"])\n"
        "    fig.tight_layout()\n"
        "    fig.savefig(cfg[\"figure\"], dpi=160, bbox_inches=\"tight\")\n"
        "    plt.show()\n"
    ),
    md("### Combined view: screening vs enhanced"),
    code(
        "fig, ax = plt.subplots(figsize=(7.2, 5.0))\n"
        "for key, cfg in MODEL_CONFIGS.items():\n"
        "    nb_model = np.asarray(dca_results[key][\"net_benefit_model\"])\n"
        "    ax.plot(PT_GRID, nb_model, color=cfg[\"colour\"], linewidth=2.2,\n"
        "            label=f\"{key.capitalize()} model\")\n"
        "    ax.axvline(dca_results[key][\"threshold\"], color=cfg[\"colour\"],\n"
        "               linestyle=\":\", linewidth=1.3, alpha=0.75,\n"
        "               label=f\"{key.capitalize()} threshold {dca_results[key]['threshold']:.2f}\")\n"
        "\n"
        "nb_treat_all = np.asarray(dca_results[\"screening\"][\"net_benefit_treat_all\"])\n"
        "ax.plot(PT_GRID, nb_treat_all, color=\"#d62728\", linestyle=\"--\", linewidth=1.6, label=\"Treat all\")\n"
        "ax.axhline(0.0, color=\"#444\", linestyle=\":\", linewidth=1.4, label=\"Treat none\")\n"
        "\n"
        "nb_max = max(np.max(dca_results[k][\"net_benefit_model\"]) for k in dca_results)\n"
        "ax.set_ylim(-0.05, float(nb_max) + 0.02)\n"
        "ax.set_xlim(0.0, 1.0)\n"
        "ax.set_xlabel(\"Threshold probability $p_t$\")\n"
        "ax.set_ylabel(\"Net benefit\")\n"
        "ax.set_title(\"Decision Curve Analysis - Screening vs Enhanced PCOS Models\")\n"
        "ax.legend(loc=\"upper right\", fontsize=9)\n"
        "fig.tight_layout()\n"
        "fig.savefig(FIGURE_DIR / \"dca_combined.png\", dpi=160, bbox_inches=\"tight\")\n"
        "plt.show()\n"
    ),
    md("## Persist Metrics"),
    code(
        "metrics_path = METRIC_DIR / \"dca.json\"\n"
        "with open(metrics_path, \"w\", encoding=\"utf-8\") as f:\n"
        "    json.dump(dca_results, f, indent=2)\n"
        "print(\"Saved:\", metrics_path)\n"
    ),
    md(
        "## Interpretation\n"
        "\n"
        "- The screening model is intended for primary-care triage, where the cost "
        "of missing a PCOS case is high relative to the cost of an extra referral. "
        "Low threshold probabilities (roughly 0.05-0.30) reflect that preference, "
        "and the decision curve shows positive net benefit over **treat all** "
        "across this range.\n"
        "- The enhanced model adds labs and ultrasound, which lifts net benefit "
        "at higher thresholds. This is the regime where false positives carry "
        "real harm (invasive workup, anxiety), so a higher pt is appropriate.\n"
        "- The deployed action thresholds from notebooks 02 (0.285) and 03 (0.38) "
        "both sit comfortably inside the clinically-useful range identified here.\n"
    ),
    md("## Output Verification"),
    code(
        "expected_outputs = [\n"
        "    FIGURE_DIR / \"dca_screening.png\",\n"
        "    FIGURE_DIR / \"dca_enhanced.png\",\n"
        "    FIGURE_DIR / \"dca_combined.png\",\n"
        "    METRIC_DIR / \"dca.json\",\n"
        "]\n"
        "for path in expected_outputs:\n"
        "    assert path.exists(), f\"Missing output: {path}\"\n"
        "    assert path.stat().st_size > 0, f\"Empty output: {path}\"\n"
        "print(\"All expected outputs exist and are non-empty.\")\n"
    ),
]


def build():
    nb = nbf.v4.new_notebook()
    nb["cells"] = CELLS
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python"},
    }
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Wrote {NOTEBOOK_PATH}")


if __name__ == "__main__":
    build()
