"""PCOS Pathfinder - Streamlit prototype.

Run from the project root:
    streamlit run src/app.py

Loads the joblib artifacts produced by notebooks 02, 03, and 04. Renders the
three-tab clinician workflow described in PROJECT_PLAN.md.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "outputs" / "models"

SCREENING_PATH = MODEL_DIR / "pcos_screening_model.joblib"
ENHANCED_PATH = MODEL_DIR / "pcos_enhanced_model.joblib"
ENDO_PATH = MODEL_DIR / "endometriosis_overlap_model.joblib"


@st.cache_resource
def load_artifacts():
    missing = [p for p in [SCREENING_PATH, ENHANCED_PATH, ENDO_PATH] if not p.exists()]
    if missing:
        st.error(
            "Model artifacts are missing. Run notebooks 02, 03, and 04 first.\n\n"
            + "\n".join(f"- {p}" for p in missing)
        )
        st.stop()
    return {
        "screening": joblib.load(SCREENING_PATH),
        "enhanced": joblib.load(ENHANCED_PATH),
        "endo": joblib.load(ENDO_PATH),
    }


def risk_tier(probability: float, threshold: float) -> tuple[str, str]:
    high_cutoff = min(0.90, threshold + 0.20)
    if probability < threshold:
        return "Low", "green"
    if probability < high_cutoff:
        return "Moderate", "orange"
    return "High", "red"


def predict(artifact: dict, row: dict) -> tuple[float, float]:
    features = artifact["features"]
    model = artifact["model"]
    threshold = float(artifact["threshold"])
    X = pd.DataFrame([row])[features]
    prob = float(model.predict_proba(X)[:, 1][0])
    return prob, threshold


def transform_through_preprocessing(model, X_row):
    X = X_row.copy()
    for _, transformer in model.steps[:-1]:
        X = transformer.transform(X)
    return X


def explain_patient(artifact: dict, row: dict, top_n: int = 6) -> pd.DataFrame | None:
    try:
        import shap
    except ImportError:
        return None

    features = artifact["features"]
    model = artifact["model"]
    estimator = model.named_steps["model"]
    X_row = pd.DataFrame([row])[features]
    X_t = transform_through_preprocessing(model, X_row)

    try:
        if hasattr(estimator, "feature_importances_"):
            explainer = shap.TreeExplainer(estimator)
            sv = explainer.shap_values(X_t)
            if isinstance(sv, list):
                values = sv[1][0] if len(sv) > 1 else sv[0][0]
            elif np.ndim(sv) == 3:
                values = sv[0, :, 1]
            else:
                values = sv[0]
        elif hasattr(estimator, "coef_"):
            background = artifact.get("shap_background_transformed")
            if background is None or len(background) < 2:
                # Without a multi-row background, LinearExplainer collapses to
                # something uninformative; degrade gracefully.
                return None
            explainer = shap.LinearExplainer(estimator, background)
            values = np.array(explainer.shap_values(X_t))[0]
        else:
            return None
    except Exception:
        return None

    table = pd.DataFrame({
        "feature": features,
        "patient value": X_row.iloc[0].values,
        "log-odds contribution": values,
    })
    table["direction"] = np.where(table["log-odds contribution"] > 0, "↑ PCOS", "↓ PCOS")
    table["abs"] = table["log-odds contribution"].abs()
    return table.sort_values("abs", ascending=False).drop(columns="abs").head(top_n).reset_index(drop=True)


def patient_intake_form() -> dict:
    yn = {"No": 0, "Yes": 1}

    st.subheader("Patient intake (primary care)")
    cols = st.columns(3)
    with cols[0]:
        age = st.number_input("Age (years)", 12, 80, 28)
        bmi = st.number_input("BMI", 12.0, 60.0, 24.0, step=0.1)
        cycle_choice = st.selectbox("Cycle pattern", ["Regular (cycle ~28d)", "Irregular"])
        cycle_r_i = 2 if cycle_choice.startswith("Regular") else 5
        # The source column labelled "Cycle length(days)" in the Kaggle data is
        # actually duration of menses bleeding in days (range 0-12, median 5),
        # not the menstrual cycle interval. The UI surfaces it as such.
        cycle_length = st.number_input(
            "Duration of menses bleeding (days)", 0, 12, 5,
            help="The source dataset's 'cycle length' column is bleeding duration, not cycle interval.",
        )
    with cols[1]:
        weight_gain = yn[st.selectbox("Recent weight gain", ["No", "Yes"])]
        hair_growth = yn[st.selectbox("Excess facial/body hair", ["No", "Yes"])]
        skin_darkening = yn[st.selectbox("Skin darkening", ["No", "Yes"])]
        hair_loss = yn[st.selectbox("Hair loss / thinning", ["No", "Yes"])]
        pimples = yn[st.selectbox("Persistent acne", ["No", "Yes"])]
    with cols[2]:
        rbs = st.number_input("RBS (mg/dl)", 0, 500, 90)
        bp_sys = st.number_input("BP systolic (mmHg)", 0, 250, 120)
        bp_dia = st.number_input("BP diastolic (mmHg)", 0, 200, 80)

    with st.expander("Labs and ultrasound (enhanced diagnostic support)"):
        c1, c2, c3 = st.columns(3)
        with c1:
            hb = st.number_input("Hb (g/dl)", 0.0, 20.0, 12.0, step=0.1)
            fsh = st.number_input("FSH (mIU/mL)", 0.0, 100.0, 5.0, step=0.1)
            lh = st.number_input("LH (mIU/mL)", 0.0, 100.0, 5.0, step=0.1)
            tsh = st.number_input("TSH (mIU/L)", 0.0, 100.0, 2.5, step=0.1)
        with c2:
            amh = st.number_input("AMH (ng/mL)", 0.0, 50.0, 3.0, step=0.1)
            prl = st.number_input("Prolactin (ng/mL)", 0.0, 100.0, 12.0, step=0.1)
            vit_d = st.number_input("Vitamin D3 (ng/mL)", 0.0, 150.0, 25.0, step=0.1)
            prg = st.number_input("Progesterone (ng/mL)", 0.0, 50.0, 1.0, step=0.1)
        with c3:
            foll_l = st.number_input("Follicle count L", 0, 50, 5)
            foll_r = st.number_input("Follicle count R", 0, 50, 5)
            f_size_l = st.number_input("Avg follicle size L (mm)", 0.0, 30.0, 14.0, step=0.5)
            f_size_r = st.number_input("Avg follicle size R (mm)", 0.0, 30.0, 14.0, step=0.5)
            endo_mm = st.number_input("Endometrium (mm)", 0.0, 30.0, 8.0, step=0.5)

    with st.expander("Differential workup (endometriosis-overlap prompt)"):
        c1, c2 = st.columns(2)
        with c1:
            mi_diff = yn[st.selectbox("Menstrual irregularity", ["No", "Yes"], key="diff_mi")]
            chronic_pain = st.slider("Chronic pain level (0-10)", 0, 10, 0)
        with c2:
            horm_abn = yn[st.selectbox("Hormone-level abnormality", ["No", "Yes"], key="diff_ha")]
            infertility = yn[st.selectbox("Reported infertility", ["No", "Yes"], key="diff_inf")]

    return {
        "age_yrs": age,
        "bmi": bmi,
        "cycle_r_i": cycle_r_i,
        "cycle_irregular_flag": 1 if cycle_r_i >= 4 else 0,
        "cycle_length_days": cycle_length,
        "weight_gain_y_n": weight_gain,
        "hair_growth_y_n": hair_growth,
        "skin_darkening_y_n": skin_darkening,
        "hair_loss_y_n": hair_loss,
        "pimples_y_n": pimples,
        "rbs_mg_dl": rbs,
        "bp_systolic_mmhg": bp_sys,
        "bp_diastolic_mmhg": bp_dia,
        "hb_g_dl": hb,
        "fsh_miu_ml": fsh,
        "lh_miu_ml": lh,
        "fsh_lh": (fsh / lh) if lh > 0 else 0.0,
        "tsh_miu_l": tsh,
        "amh_ng_ml": amh,
        "prl_ng_ml": prl,
        "vit_d3_ng_ml": vit_d,
        "prg_ng_ml": prg,
        "follicle_no_l": foll_l,
        "follicle_no_r": foll_r,
        "avg_f_size_l_mm": f_size_l,
        "avg_f_size_r_mm": f_size_r,
        "endometrium_mm": endo_mm,
        "age": age,
        "menstrual_irregularity": mi_diff,
        "chronic_pain_level": chronic_pain,
        "hormone_level_abnormality": horm_abn,
        "infertility": infertility,
    }


def render_pcos_result(label: str, caption: str, artifact: dict, row: dict) -> None:
    prob, threshold = predict(artifact, row)
    tier, color = risk_tier(prob, threshold)

    st.markdown(f"### {label}")
    st.caption(caption)
    cols = st.columns([1, 1, 1])
    cols[0].metric("PCOS probability", f"{prob:.1%}")
    cols[1].metric("Action threshold", f"{threshold:.2f}")
    cols[2].markdown(f"#### Risk tier: :{color}[**{tier}**]")

    explanation = explain_patient(artifact, row)
    if explanation is not None and not explanation.empty:
        st.markdown("**Top contributing features (SHAP, log-odds units):**")
        st.dataframe(explanation, use_container_width=True, hide_index=True)
    else:
        st.info("SHAP explanation unavailable; install `shap` to enable per-patient drivers.")


def render_endo_flag(artifact: dict, row: dict) -> None:
    features = artifact["features"]
    model = artifact["model"]
    threshold = float(artifact["threshold"])
    endo_row = {
        "age": row.get("age", row.get("age_yrs")),
        "menstrual_irregularity": row["menstrual_irregularity"],
        "chronic_pain_level": row["chronic_pain_level"],
        "hormone_level_abnormality": row["hormone_level_abnormality"],
        "infertility": row["infertility"],
        "bmi": row["bmi"],
    }
    X = pd.DataFrame([endo_row])[features]
    prob = float(model.predict_proba(X)[:, 1][0])

    st.markdown("### Endometriosis overlap (differential prompt)")
    if prob >= threshold:
        st.warning(
            f"**Symptom-overlap pattern detected** (prob={prob:.1%}, threshold={threshold:.2f}). "
            "Consider broader differential workup for endometriosis or other gynaecologic conditions. "
            "This is a synthetic-data prompt, not a diagnostic claim."
        )
    else:
        st.info(
            f"No strong endometriosis-overlap signal (prob={prob:.1%}, threshold={threshold:.2f}). "
            "Synthetic-data prompt only."
        )


def render_diagnostic_checklist(row: dict) -> None:
    """Render Rotterdam-style completeness and safety checks for the demo UI."""
    ovulatory_dysfunction = row["cycle_irregular_flag"] == 1
    clinical_hyperandrogenism = bool(
        row["hair_growth_y_n"] or row["pimples_y_n"] or row["hair_loss_y_n"]
    )
    ultrasound_pattern = bool(row["follicle_no_l"] >= 12 or row["follicle_no_r"] >= 12)
    metabolic_context = bool(
        row["bmi"] >= 25
        or row["rbs_mg_dl"] >= 140
        or row["bp_systolic_mmhg"] >= 130
        or row["bp_diastolic_mmhg"] >= 80
    )

    st.markdown("### Diagnostic completeness and safety checks")
    st.caption(
        "Workflow checklist for discussion, not a formal diagnosis. "
        "The source dataset does not include testosterone, so biochemical hyperandrogenism remains a missing test."
    )

    checklist = pd.DataFrame(
        [
            {
                "check": "Ovulatory dysfunction signal",
                "status": "Present" if ovulatory_dysfunction else "Not evident",
                "entered evidence": "Irregular cycle pattern" if ovulatory_dysfunction else "Regular cycle pattern",
            },
            {
                "check": "Clinical hyperandrogenism signal",
                "status": "Present" if clinical_hyperandrogenism else "Not evident",
                "entered evidence": "Hirsutism/acne/hair-loss symptom entered"
                if clinical_hyperandrogenism
                else "No hyperandrogenic symptom entered",
            },
            {
                "check": "Polycystic-ovary morphology prompt",
                "status": "Present" if ultrasound_pattern else "Not evident",
                "entered evidence": f"Follicle counts L/R: {row['follicle_no_l']}/{row['follicle_no_r']}",
            },
            {
                "check": "Metabolic follow-up prompt",
                "status": "Consider" if metabolic_context else "No immediate prompt",
                "entered evidence": f"BMI {row['bmi']:.1f}, RBS {row['rbs_mg_dl']}, BP {row['bp_systolic_mmhg']}/{row['bp_diastolic_mmhg']}",
            },
        ]
    )
    st.dataframe(checklist, use_container_width=True, hide_index=True)

    if 18.5 <= row["bmi"] < 25:
        st.warning(
            "Fairness note: validation found lower screening recall in the normal-BMI subgroup. "
            "Do not rule out lean PCOS solely from a low screening probability when symptoms persist."
        )


def render_population_view(artifacts: dict) -> None:
    """Show the cohort-level signals captured in outputs/metrics."""
    st.subheader("Population view (source cohort)")
    st.caption(
        "Aggregate signals computed on the full source cohort (n=541) "
        "before the train/test split, useful for outreach planning."
    )

    rates_path = PROJECT_ROOT / "outputs" / "metrics" / "pcos_symptom_rates.csv"
    if rates_path.exists():
        rates = pd.read_csv(rates_path, index_col=0)
        st.markdown("**Symptom prevalence by PCOS status (source cohort):**")
        st.dataframe(rates, use_container_width=True)
    else:
        st.info("Run notebook 01 to populate population-level signals.")

    cols = st.columns(2)
    cols[0].metric("Screening model AUC", f"{artifacts['screening']['metrics']['roc_auc']:.3f}")
    cols[0].metric("Screening recall", f"{artifacts['screening']['metrics']['recall']:.1%}")
    cols[1].metric("Enhanced model AUC", f"{artifacts['enhanced']['metrics']['roc_auc']:.3f}")
    cols[1].metric("Enhanced recall", f"{artifacts['enhanced']['metrics']['recall']:.1%}")


def main() -> None:
    st.set_page_config(page_title="PCOS Pathfinder", layout="wide")
    st.title("PCOS Pathfinder")
    st.caption(
        "Tiered clinical decision support for earlier PCOS detection and differential diagnosis. "
        "**Decision support, not standalone diagnosis.**"
    )

    artifacts = load_artifacts()

    tab_assess, tab_population, tab_about = st.tabs(["Patient assessment", "Population view", "About"])

    with tab_assess:
        row = patient_intake_form()
        if st.button("Run assessment", type="primary"):
            st.divider()
            render_pcos_result(
                "Frontline screening",
                "Uses only symptoms and basic vitals - suitable for primary care or telehealth.",
                artifacts["screening"],
                row,
            )
            st.divider()
            render_pcos_result(
                "Enhanced diagnostic support",
                "Uses labs and ultrasound in addition to screening features.",
                artifacts["enhanced"],
                row,
            )
            st.divider()
            render_diagnostic_checklist(row)
            st.divider()
            render_endo_flag(artifacts["endo"], row)
            st.divider()
            st.caption(
                "Models trained on a single Kerala (India) hospital cohort (n=541, PCOS positives=177). "
                "External validation is required before any clinical deployment."
            )

    with tab_population:
        render_population_view(artifacts)

    with tab_about:
        st.markdown(
            """
            **PCOS Pathfinder** is a Biohackathon 2026 prototype.

            - **Frontline screening model** uses only symptoms and basic vitals.
            - **Enhanced model** adds labs (FSH, LH, AMH, TSH, PRL, ...) and ultrasound findings.
            - **Endometriosis-overlap module** prompts a broader differential when symptoms overlap.
              The underlying dataset is synthetic, so this is a workflow prompt, not a diagnostic claim.

            Thresholds were chosen via 5-fold cross-validation on the training set targeting recall ≥ 0.90,
            then evaluated once on a held-out test split. See `outputs/metrics/pcos_model_card.md` for the full card.
            """
        )


if __name__ == "__main__":
    main()
