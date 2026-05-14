# PCOS Pathfinder 12-Minute Presentation Script

Target length: 12 minutes  
Deck: `presentation/pcos_pathfinder_deck.html`  
Tone: clinical, practical, evidence-first.

## Slide 1 - Title (0:00-0:40)

Good morning. We built **PCOS Pathfinder**: a tiered, explainable decision-support workflow for earlier PCOS detection and safer differential workup.

The main idea is that clinical AI should not just output a label. It should help a clinician decide who needs follow-up, explain the evidence behind the risk score, and avoid missing overlapping conditions.

On the held-out PCOS split, the enhanced model reaches **0.953 ROC-AUC**, with **0.886 sensitivity** and **0.902 specificity**. The project is reproducible from **13 executed notebooks** and includes a working Streamlit prototype.

## Slide 2 - The Diagnostic Gap (0:40-1:35)

PCOS is difficult because it is not one clean symptom or one single test. A patient may present with irregular bleeding, acne, hair growth, weight change, infertility, metabolic abnormalities, or ultrasound findings.

Those clues are often seen at different times and by different parts of the healthcare system. Primary care may see early symptoms before labs or ultrasound are ordered. Gynecology may see reproductive concerns later. Endocrinology may see metabolic or hormonal patterns.

So the problem is not just prediction. The problem is synthesis: helping clinicians combine scattered signals into a safer next step.

## Slide 3 - Tiered Workflow (1:35-2:30)

PCOS Pathfinder follows the way evidence arrives clinically.

First, the **frontline screening model** uses symptoms and basic vitals only. This makes it usable in primary care, telehealth, or low-resource settings.

Second, the **enhanced diagnostic-support model** adds labs and ultrasound when those are available.

Third, the app shows a **diagnostic-completeness checklist**: Rotterdam-style evidence, missing biochemical hyperandrogenism testing, metabolic follow-up prompts, and a lean-PCOS safety warning.

Fourth, the **endometriosis-overlap prompt** nudges broader workup when symptoms such as chronic pain and infertility cluster with menstrual irregularity. It is intentionally framed as a workflow prompt, not a diagnosis.

## Slide 4 - Data Foundation (2:30-3:35)

The required PCOS clinical dataset is the modelling foundation. It contains **541 patients**, with **177 PCOS-positive** and **364 non-PCOS** records.

The supplementary endometriosis dataset has **10,000 synthetic rows**, so it is used only for symptom-overlap prompting. The single-cell archives are used only as biological context: notebook 06 checks whether curated PCOS-relevant genes appear in the first available PCOS feature list. We do not claim single-cell expression analysis.

One important data-quality correction is the source field labelled **Cycle length(days)**. It ranges from zero to twelve, with a median around five, so it represents **duration of menses bleeding**, not a normal menstrual-cycle interval. The app therefore labels the input correctly and prevents a clinician from entering a typical 28-day value that would be out-of-distribution.

Cleaning also drops identifiers, blood group, and marriage-status years. Lifestyle proxies like fast food and exercise are excluded from the screening feature set because they are bias-prone and hard to validate at intake.

## Slide 5 - Model Design (3:35-4:35)

We train three models, each with a specific clinical role.

The **screening model** is a Random Forest using 13 basic features: age, BMI, menstrual pattern, bleeding duration, symptoms, random blood sugar, and blood pressure.

The **enhanced model** is a Random Forest using 27 features, adding hormones and ultrasound findings such as FSH, LH, AMH, follicle counts, follicle size, and endometrium thickness.

The **endometriosis-overlap model** is logistic regression using six synthetic-dataset features. It exists only to prompt differential thinking.

For validation, model selection uses five-fold stratified cross-validation on the training split. Action thresholds are chosen from out-of-fold training probabilities, not from the test set. The held-out test split is evaluated once at the end.

## Slide 6 - Held-Out Results (4:35-5:35)

The screening model reaches **0.896 AUC** and catches **39 of 44 PCOS-positive patients** in the holdout cohort. Its sensitivity is **0.886**, and its negative predictive value is **0.926**.

The enhanced model keeps the same sensitivity, **0.886**, but improves specificity from **0.685 to 0.902** and precision from **0.574 to 0.812**. Its AUC is **0.953**, and its F2 score is **0.871**.

This is exactly what the tiered pathway should do. The first model screens broadly. The second model uses richer clinical evidence to reduce false positives without losing sensitivity.

The endometriosis module has **0.660 AUC**, which is modest and appropriate for a synthetic-data prompt. We do not present it as a validated diagnostic model.

## Slide 7 - Uncertainty and Calibration (5:35-6:30)

Point estimates alone are not enough for a clinical prediction story, so we added a rigor layer.

Notebook 07 computes **2000-resample bootstrap confidence intervals**. The enhanced model's AUC advantage over screening is **+0.057**, with a 95 percent interval from **+0.013 to +0.105**.

Notebook 08 checks calibration. For the enhanced model, Platt scaling improves the Brier score from **0.093 to 0.072**, and expected calibration error from **0.143 to 0.045**.

Notebook 12 adds split-conformal prediction. At a target coverage of 0.90, empirical holdout coverage is **0.912**. If the conformal prediction set is empty, that should be treated as an abstention requiring clinician review.

## Slide 8 - Clinical Utility and Safety (6:30-7:25)

Decision curve analysis asks a clinically important question: does the model help at plausible action thresholds?

Both selected thresholds sit inside useful net-benefit ranges compared with treat-all and treat-none baselines. That means the thresholds are not only statistically convenient; they are aligned with a reasonable decision-support use case.

We also ran a subgroup recall audit. The screening model has a **25-point BMI recall gap**, with lower recall in the normal-BMI subgroup. This matters because lean PCOS is a known clinical concern. Rather than hide the gap, the prototype warns clinicians not to rule out PCOS solely from a low screening probability when symptoms persist.

## Slide 9 - Patient-Level Explainability (7:25-8:15)

The app is designed so a clinician can inspect the reason behind a risk score.

Each PCOS result shows the predicted probability, the action threshold, the risk tier, and the top patient-level SHAP contributors in log-odds units.

For the held-out positive case shown here, the enhanced model is driven strongly by follicle counts, which is clinically sensible. The screening model leans more on symptoms and basic vitals, as expected.

The checklist then translates that risk score into a clinical evidence review: what supports PCOS, what is missing, whether metabolic follow-up is needed, and when lean-PCOS caution should remain active.

## Slide 10 - External Benchmarks (8:15-9:10)

We benchmarked the selected Random Forest models against both modern machine learning and clinical rules.

TabPFN-v2 reaches **0.905 AUC** on the screening feature set and **0.962 AUC** on the enhanced feature set. That confirms the dataset is close to ceiling for small-tabular prediction. But at our selected action thresholds, TabPFN trades away recall and is slower on CPU, so Random Forest remains the more practical deployed model.

We also compare the enhanced model against a hand-coded Rotterdam-style 2-of-3 rule on the same holdout split. The enhanced model adds **9.1 sensitivity points** with a **1.1 specificity-point cost**.

The limitation is explicit: the dataset does not include direct serum testosterone, so biochemical hyperandrogenism must be approximated.

## Slide 11 - Differential Diagnosis Prompt (9:10-9:55)

The differential prompt is deliberately modest, but clinically useful.

It uses six features: age, BMI, menstrual irregularity, chronic pain, hormone-level abnormality, and infertility. When the overlap pattern crosses threshold, the app prompts the clinician to consider broader gynecologic workup.

The key design choice is restraint. Because the endometriosis data is synthetic, we do not claim clinical diagnosis. We use it to prevent tunnel vision. The system says, in effect: PCOS may be high risk, but do not ignore overlapping conditions when the symptom pattern warrants it.

## Slide 12 - Implementation Path (9:55-10:55)

The implementation is already usable as a prototype.

The Streamlit app loads the same joblib artifacts produced by notebooks 02, 03, and 04. The repository includes 13 executed notebooks, deterministic notebook builders, exported metrics and figures, cleaned data, saved models, a model card, README, and submission checklist.

For real clinical use, the next steps are clear. First, validate on partner clinical data. Second, run the tool silently beside usual care and measure whether it changes referral timing. Third, evaluate prospectively with calibration, subgroup recall, and clinical outcome monitoring before any deployment claim.

## Slide 13 - Patient and System Impact (10:55-12:00)

The practical impact is earlier, clearer next steps.

For primary care, PCOS Pathfinder identifies patients who need PCOS assessment before years of delay. For low-resource settings, the first model uses symptoms and basic vitals only. For clinicians, the enhanced model adds labs and ultrasound without hiding the tradeoffs. For patient safety, the system includes SHAP, calibration, conformal uncertainty, subgroup warnings, and explicit limitations.

The closing message is simple: **PCOS Pathfinder is not trying to replace diagnosis. It helps clinicians choose the next investigation earlier, with clearer evidence and safer guardrails.**
