# Biohackathon 2026 Women's Health Project Plan

## Project Title

**PCOS Pathfinder: A Tiered Clinical Decision Support Tool for Earlier PCOS Detection and Differential Diagnosis**

## Executive Summary

This project will build a feasible, data-grounded decision-support system that helps clinicians identify patients at risk of Polycystic Ovary Syndrome (PCOS), interpret complex symptom and clinical patterns, and reduce delayed or missed diagnosis.

The solution will use the required PCOS clinical dataset as the foundation. It will also use the supplementary endometriosis dataset to frame symptom overlap and differential diagnosis. The single-cell datasets will be treated as optional biological context rather than the core modeling task, because the main judging criteria favor clinical usefulness, feasibility, diagnostic accuracy, and implementation.

The final deliverable should be a reproducible codebase, a simple prototype or dashboard, and a concise slide deck showing clinical rationale, data methodology, model performance, explainability, limitations, and real-world implementation.

## Canva Briefing Summary

Source deck:

`https://www.canva.com/design/DAHJEqUFaiI/a0TXIeqQvaRvfwF493mkcw/view`

Deck title:

**Biohackathon 2026: Women's Health**

Event dates:

**11 May 2026 to 22 May 2026**

### Deck-Level Summary

The Canva deck is a participant briefing for Biohackathon 2026. The main challenge is to develop a feasible system or method that improves diagnostic accuracy for women's health conditions, using PCOS as the required core use case.

The challenge emphasizes that PCOS is common, heterogeneous, frequently delayed or missed, and representative of broader diagnostic gaps in women's health. Participants are expected to use the main PCOS clinical dataset as the foundation of their project. Supplementary datasets, including endometriosis and single-cell datasets, may be used to strengthen differential diagnosis, biological rationale, or broader clinical framing.

The strongest project should show:

- A clear clinical problem and patient impact.
- Use of the required PCOS dataset.
- Practicality in real healthcare workflows.
- Ability to support clinicians, not replace them.
- Attention to diagnostic disparities.
- Clear methodology, validation, and implementation steps.
- A polished final presentation and code submission.

Important note:

The judging weights shown in the deck appear to sum to 110% if read literally:

- Clinical and Scientific Validity: 30%
- Diagnostic Accuracy: 20%
- Feasibility and Implementation: 20%
- Innovation and Creativity: 12%
- Impact and Public Health Value: 10%
- Methodology and Scientific Rigor: 10%
- Code Quality and Technical Execution: 5%
- Presentation and Clarity: 3%

This should be treated carefully in the presentation. The safest approach is to optimize for the major categories while not calling out the arithmetic issue unless asked.

### Scraped Slide-by-Slide Digest

#### Slide 1: Title

- Biohackathon 2026: Women's Health
- Dates: 11 May 2026 to 22 May 2026

#### Slide 2: Overall Timeline

- 11 May 2026: Start of hackathon and release of challenge details and format.
- 12-13 May 2026: Guest speaker sessions in the morning and afternoon.
- 13-19 May 2026: Consultation available by committee members.
- 20 May 2026: Submission date for code, slides, and any self-sourced datasets.
- 21-22 May 2026: Q&A and presentation days.

#### Slide 3: Problem Statement Background

- PCOS is presented as a microcosm of a larger problem in women's health.
- Common, heterogeneous, and poorly understood conditions can lead to delayed or missed diagnoses.
- These problems disproportionately affect marginalized populations.
- Early diagnosis matters because metabolic interventions work best when implemented early.
- Patients deserve timely answers about their health.

#### Slide 4: Challenge Statement

Participants must develop a feasible system or method to improve diagnostic accuracy for women's health conditions.

The solution should:

- Help clinicians interpret complex symptoms.
- Reduce missed or incorrect diagnoses.
- Help differentiate PCOS from similar or overlapping conditions.
- Use available data.
- Be practical for real-world healthcare settings.
- Address diagnostic disparities across populations.
- Demonstrate impact on patient outcomes.
- Outline implementation steps.

#### Slide 5: Dataset Details Overview

- Several datasets are provided.
- The main PCOS dataset is required as the foundation of the project.
- Supplementary and single-cell datasets may be used to strengthen analysis, explore related conditions, or support biological rationale.

#### Slide 6: Dataset List

Provided datasets:

- Main Dataset: PCOS physical and clinical parameters.
- Supplementary Dataset: Endometriosis features and symptoms.
- Single-Cell Datasets: PCOS-related and endometrium-related single-cell datasets.

Participant guidance:

- The main dataset forms the project core.
- Additional datasets can supplement, compare, or expand the solution.

#### Slide 7: Main PCOS Dataset

- Dataset: PCOS Physical and Clinical Parameters.
- Description: Physical and clinical parameters related to PCOS diagnosis.
- Data source: 10 hospitals across Kerala, India.
- Suggested use: Core dataset for clinical pattern analysis, risk prediction, model development, and team comparison.
- Access: Kaggle PCOS dataset and provided Excel sheet.

#### Slide 8: Supplementary Endometriosis Dataset

- Dataset: Endometriosis Features and Symptoms.
- Description: 10,000 synthetic but realistic instances reflecting common endometriosis-related symptoms and features.
- Suggested use: Differential diagnosis, symptom-overlap analysis, and comparison between PCOS and related or overlapping conditions.
- Example features:
  - Age
  - Menstrual irregularity
  - Chronic pain level
  - Hormone level abnormality
  - Infertility
  - BMI
  - Diagnosis label

#### Slide 9: PCOS-Related Single-Cell Dataset

- Dataset: PCOS-related single-cell dataset.
- Description: Single-cell RNA sequencing data related to pathways and genes contributing to hyperandrogenemia associated with PCOS.
- Suggested use:
  - Gene and pathway exploration.
  - Biological mechanism analysis.
  - Biomarker discovery.
  - Scientific rationale for the proposed solution.
- Available sample groups:
  - PCOS-affected samples.
  - Normal cycling women samples.
  - Forskolin-treated samples.
  - Untreated control samples.

#### Slide 10: Endometrium-Related Single-Cell Dataset

- Dataset: Endometrium-related single-cell dataset.
- Description: Endometrial samples from reproductive-age donors with and without endometriosis, collected during natural cycles or under exogenous hormonal treatment.
- Suggested use:
  - Explore endometriosis-related biology.
  - Compare overlapping reproductive conditions.
  - Support differential diagnosis discussion.

#### Slide 11: Judging Criteria, Part 1

Clinical and Scientific Validity: 30%

Judges may consider:

- Reflection of current PCOS biology and pathophysiology.
- Engagement with existing diagnostic frameworks or classification approaches.
- Effectiveness in distinguishing PCOS from overlapping or related conditions.
- Strength of scientific justification through literature, clinical rationale, or mechanistic reasoning.

Diagnostic Accuracy: 20%

Judges may consider:

- Ability to improve differentiation between PCOS and overlapping conditions.
- Support for clinical interpretation, decision-making, or investigation prioritization.
- Usefulness for early identification, risk prediction, or screening.
- Ability to account for patient heterogeneity, including phenotypes, symptoms, and comorbidities.

#### Slide 12: Judging Criteria, Part 2

Feasibility and Implementation: 20%

Judges may consider:

- Applicability across clinical environments such as primary care, specialist clinics, telehealth, and community settings.
- Accessibility, affordability, scalability, and usability.
- Practicality of required data inputs, devices, infrastructure, and workflows.
- Adaptability to low-resource or data-limited settings.

Innovation and Creativity: 12%

Judges may consider:

- Novelty of perspective, workflow, methodology, or application.
- Creative reframing of the problem.
- Meaningful difference from existing solutions.

Impact and Public Health Value: 10%

Judges may consider:

- Influence on long-term health outcomes and quality of life.
- Relevance to diverse or underserved populations.
- Preventive, educational, or early intervention value.
- Scalability and public health reach.

#### Slide 13: Judging Criteria, Part 3

Methodology and Scientific Rigor: 10%

Judges may consider:

- Alignment with the stated objectives.
- Clear justification of analytical, computational, or research approaches.
- Suitable validation, benchmarking, or evaluation strategies.

Code Quality and Technical Execution: 5%

Judges may consider:

- Documentation, comments, and instructions.
- Robust data handling and preprocessing.
- Readability, maintainability, and reproducibility.

Presentation and Clarity: 3%

Judges may consider:

- Clear explanation of problem, solution, and methodology.
- Logical organization.
- Use of demonstrations, visualizations, prototypes, or interactive elements.

#### Slide 14: Speaker Lineup, 12 May 2026

- Prof Li Jingmei, Assistant Director, Population Health at A*STAR; Group Leader, Lab of Women's Health and Genetics at A*STAR. Time: 10:00 AM to 10:30 AM.
- Assoc Prof Joanne Ngeow, Associate Professor of Genomic Medicine at Lee Kong Chian School of Medicine and Senior Consultant, Division of Medical Oncology at National Cancer Centre Singapore. Time: 10:30 AM to 11:00 AM.
- Mr Joshua Yim, Founder and CEO at Navo Health. Navo Health focuses on AI-enabled fetal monitoring and safer childbirth. Time: 2:00 PM to 2:30 PM.

#### Slide 15: Speaker Lineup, 13 May 2026

- Dr Alvin Ng Wei Tian, Dean's Post-Doctoral Fellow at Lee Kong Chian School of Medicine. He is a computational biologist focusing on cancer genomics and sequencing-based analysis. Time: 10:00 AM to 10:30 AM.
- Assoc Prof Melissa Fullwood, Associate Professor and Director of Master's Programme at the School of Biological Sciences. Her work spans artificial intelligence, biomedical data science, and epigenomic and transcriptomic regulation. Time: 11:00 AM to 11:30 AM.

#### Slide 16: Judges, 21 May 2026

- Dr Kimberle Shen.
- Prof Chan Wei Ting, Samantha.
- Dr Vidya Sudarshan.
- Prof Melanie Herschel.

#### Slide 17: Judges, 22 May 2026

- Prof Anni Zhang.
- Prof Chan Wei Ting, Samantha.
- Dr Vidya Sudarshan.
- Prof Melanie Herschel.

#### Slide 18: Prizes

- First place: $240 Grab vouchers to be split among the whole team.
- Second place: $160 Grab vouchers to be split among the whole team.
- Third place: $100 Grab vouchers to be split among the whole team.
- Honourable mentions: $20 Grab vouchers to be split among the whole team, five awards.

#### Slide 19: Telegram Channel

- A Telegram channel will be used for official announcements and updates.
- Participants should join the channel for important information.
- Questions should be asked using the "Ask Us Anything" topic.
- Participants are encouraged to stay active during the two-week hackathon.

#### Slide 20: Compulsory Forms

- 11 May: Attendance Form.
- 12-22 May: Progress and Attendance Check-In Form.
- These forms are compulsory for all participants.
- Participants should look out for daily progress highlights in the channel.

#### Slide 21: Presentations

Presentation schedule:

- Day 1, 21 May 2026:
  - 10:00 AM to 12:00 PM: Presentations and Q&A.
  - 2:00 PM to 4:00 PM: Presentations and Q&A.
- Day 2, 22 May 2026:
  - 10:00 AM to 12:00 PM: Presentations and Q&A.
  - 2:00 PM to 2:40 PM: Presentations and Q&A.
  - 3:00 PM to 4:00 PM: Closing ceremony.

Each team has:

- 9 minutes to present.
- 3 minutes for Q&A.

Attendance requirement:

- Attend assigned presentation slot.
- Attend closing ceremony on 22 May, 3:00 PM to 4:00 PM.

#### Slide 22: Closing

- Thank you.

## Problem Framing

PCOS is a strong example of a broader issue in women's health: common and heterogeneous conditions are frequently diagnosed late or missed entirely. PCOS diagnosis is difficult because symptoms vary across patients, no single test confirms the condition, and clinicians must synthesize menstrual, metabolic, hormonal, ovarian, dermatologic, and reproductive information.

The project should not simply be "a model that predicts PCOS." A stronger framing is:

> How can we help clinicians identify patients who need further PCOS assessment earlier, explain why they are at risk, and distinguish PCOS-like presentations from overlapping women's health conditions?

This framing aligns well with the judging criteria:

- Clinical and scientific validity
- Diagnostic accuracy
- Feasibility and implementation
- Innovation
- Public health value
- Methodological rigor
- Technical execution
- Presentation clarity

## Data Inventory

### Required Main Dataset: PCOS Clinical Dataset

Local file:

`_read_extract/(Main_Dataset)_PCOS_data_without_infertility.xlsx`

Profiled structure:

- Actual data sheet: `Full_new`
- Rows with patient data: 541
- Columns: 44
- Target: `PCOS (Y/N)`
- Class distribution:
  - Non-PCOS: 364
  - PCOS: 177

Important feature groups:

- Demographics: age, weight, height, BMI, blood group
- Vitals and general markers: pulse, respiratory rate, hemoglobin, blood pressure
- Menstrual and reproductive history: cycle regularity, cycle length, pregnancy, abortions, marriage status
- Hormonal markers: beta-HCG, FSH, LH, FSH/LH, TSH, AMH, prolactin, progesterone
- Metabolic markers: random blood sugar, BMI, weight gain
- Symptoms: hair growth, skin darkening, hair loss, pimples
- Lifestyle: fast food, regular exercise
- Ultrasound markers: follicle count left/right, follicle size left/right, endometrium thickness

Initial observations:

- PCOS-positive patients show higher average BMI, AMH, LH, follicle counts, and higher rates of weight gain, hair growth, skin darkening, and pimples.
- The data has likely outliers, especially in FSH, LH, FSH/LH, and Vitamin D3.
- Missingness is low, but data validation is still needed.
- Some columns are dropped during cleaning because they cannot contribute defensibly:
  - `Sl. No` and `Patient File No.` are identifiers.
  - `Blood Group` is stored as ordinal codes 11-18, which has no meaningful order.
  - `Marriage Status (Yrs)` is clinically sensitive and a poor proxy for any diagnostic signal.
- Lifestyle proxies (`Fast food (Y/N)` and `Reg.Exercise(Y/N)`) are intentionally excluded from the screening feature set: they are bias-prone, stigmatising, and unlikely to generalise outside the training cohort.
- One non-numeric string (`'1.99.'` in `II beta-HCG`) is silently coerced to NaN during cleaning. The data audit in notebook 01 logs every such coercion to `outputs/metrics/pcos_coercion_report.csv`.
- The column labelled `Cycle length(days)` in the source workbook ranges 0-12 with a median of 5 across both classes - this is the **duration of menses bleeding in days**, not the menstrual cycle interval. The Kaggle dataset documentation is misleading on this point. The Streamlit prototype surfaces the field with the correct label so clinicians do not enter a typical 28-day cycle value (which would be out-of-distribution and silently produce wrong predictions).

### Supplementary Dataset: Endometriosis Structured Dataset

Local file:

`_read_extract/(Supplementary_Dataset)_structured_endometriosis_data.csv`

Profiled structure:

- Rows: 10,000
- Columns: 7
- Target: `Diagnosis`
- Class distribution:
  - No endometriosis: 5,921
  - Endometriosis: 4,079

Features:

- Age
- Menstrual irregularity
- Chronic pain level
- Hormone level abnormality
- Infertility
- BMI
- Diagnosis

Recommended use:

- Use this dataset for a lightweight differential diagnosis module.
- Do not claim that it clinically validates endometriosis diagnosis, because it is synthetic.
- Use it to show symptom overlap and the need for PCOS-vs-endometriosis triage logic.

### Optional Single-Cell Datasets

Local archives:

- `_read_extract/(Supplementary_Dataset)_PCOS_single_cell_data.zip`
- `_read_extract/(Supplementary_Dataset)_Endometrium_single_cell_data.zip`

Observed structure:

- PCOS archive contains multiple samples such as `Mc03-C.tar`, `Mc03-F.tar`, etc.
- Nested files are 10x-style outputs:
  - `barcodes.tsv.gz`
  - `features.tsv.gz`
  - `matrix.mtx.gz`

Implemented use (notebook 06):

- Extract gene symbols from the first sample's `features.tsv.gz` without performing any single-cell expression analysis.
- Cross-reference the gene list with a curated set of literature-supported PCOS genes covering steroidogenesis (`CYP17A1`, `CYP19A1`), insulin signalling (`INSR`, `IRS1`, `IRS2`), and PCOS GWAS hits (`DENND1A`, `THADA`, `FSHB`).
- Export `outputs/metrics/single_cell_pcos_gene_overlap.csv` for the deck's "biological rationale" slide.
- Inventory the per-sample tar files in both archives.

Deliberately out of scope: full QC, normalisation, integration, or differential expression. The judging criteria reward clinical usefulness rather than single-cell technique depth.

## Proposed Solution

Build **PCOS Pathfinder**, a clinician-facing tiered diagnostic decision-support prototype.

The tool should support three levels of clinical use:

### 1. Frontline Screening Score

Purpose:

Identify patients who should be prioritized for further PCOS evaluation using data that is easy to collect in primary care or telehealth.

Inputs:

- Age
- BMI
- Menstrual cycle pattern (regular vs. irregular) and length
- Weight gain
- Hair growth
- Skin darkening
- Hair loss
- Pimples
- Random blood sugar
- Blood pressure (systolic and diastolic)

Lifestyle proxies (`fast_food`, `reg_exercise`) are deliberately excluded - see "Methodology > Data Cleaning" for the rationale.

Output:

- Threshold-anchored risk tier (Low / Moderate / High)
- Probability score
- Recommended next clinical step
- Top SHAP drivers in log-odds units

### 2. Enhanced Diagnostic Support Score

Purpose:

Improve diagnostic confidence once labs and ultrasound data are available.

Additional inputs:

- AMH
- LH
- FSH
- FSH/LH ratio
- TSH
- Prolactin
- Follicle count left/right
- Follicle size left/right
- Endometrium thickness

Output:

- Enhanced risk score
- Clinical feature explanation
- Suggested investigation priorities

### 3. Differential Diagnosis Flag

Purpose:

Prompt clinicians when symptoms overlap with endometriosis or other women's health conditions.

Inputs:

- Menstrual irregularity
- Chronic pain level
- Hormonal abnormality
- Infertility
- BMI
- Age

Output:

- "PCOS-like pattern"
- "Endometriosis-overlap pattern"
- "Consider further differential workup"

Important wording:

This module should not diagnose endometriosis. It should flag overlap and support clinical reasoning.

## Methodology

### Data Cleaning

Steps (implemented in `clean_pcos_dataframe` inside `scripts/create_training_notebooks.mjs`, included in every notebook's setup cell):

1. Load the `Full_new` sheet from the PCOS Excel workbook.
2. Standardize column names (lowercase, snake_case, fix the `Marraige` typo, normalise `BP _`).
3. Convert all fields with `pd.to_numeric(errors="coerce")` and log every silently-coerced cell to `outputs/metrics/pcos_coercion_report.csv`.
4. Drop columns that cannot contribute defensibly:
   - `sl_no`, `patient_file_no` (identifiers)
   - `blood_group` (ordinal codes 11-18 with no meaningful order)
   - `marriage_status_yrs` (clinically sensitive, no diagnostic signal)
5. Keep binary variables encoded as 1/0 (already the source format).
6. Engineer `cycle_irregular_flag` from `cycle_r_i`: the Kaggle-style coding uses 2 for regular and 4/5 for irregular, so `flag = 1 if cycle_r_i >= 4 else 0`.
7. Cap visibly-impossible or model-dominating outliers:
   - `fsh_miu_ml` to [0, 100]
   - `lh_miu_ml` to [0, 200]
   - `fsh_lh` to [0, 50]
   - `vit_d3_ng_ml` to [0, 150]
   - `prg_ng_ml` to [0, 50]
8. Rely on median imputation inside the scikit-learn `Pipeline` (instead of imputing in-place) so the imputation rules are saved as part of the model artifact.
9. Document every drop, cap, and coercion in `outputs/metrics/`.

### Exploratory Data Analysis

Produce visuals for:

- PCOS class distribution
- Feature distributions by PCOS status
- Correlation heatmap
- Top univariate predictors
- Missingness summary
- Outlier summary
- Symptom prevalence by PCOS status
- Follicle count and AMH comparison by PCOS status

Key hypotheses to test:

- PCOS-positive patients have higher follicle counts.
- PCOS-positive patients have higher AMH.
- PCOS-positive patients have higher symptom burden across hyperandrogenism-related signs.
- A screening-only feature set can still identify high-risk patients reasonably well.
- Enhanced clinical/lab/ultrasound features improve diagnostic accuracy.

### Modeling Plan

Build two main model pipelines:

#### Model A: Screening Model

Goal:

Useful in primary care, community clinics, telehealth, or low-resource settings.

Feature set (no lifestyle proxies):

- Age
- BMI
- Cycle regularity (raw and engineered flag)
- Cycle length
- Weight gain
- Hair growth
- Skin darkening
- Hair loss
- Pimples
- RBS
- Blood pressure (systolic and diastolic)

Lifestyle indicators (`fast_food`, `reg_exercise`) are intentionally excluded. They are bias-prone, hard to validate at intake, and likely to encode confounders rather than physiology.

Candidate models (compared by 5-fold cross-validation on training data):

- Logistic regression with class-weight balancing
- Random forest with class-weight balancing
- Gradient boosting
- Dummy most-frequent baseline

Primary evaluation goal:

High sensitivity/recall for PCOS-positive cases.

#### Model B: Enhanced Diagnostic Model

Goal:

Support clinicians after labs and ultrasound results are available.

Feature set:

- Screening features
- AMH
- LH
- FSH
- FSH/LH
- TSH
- PRL
- Follicle counts
- Follicle sizes
- Endometrium thickness

Candidate models:

- Logistic regression with regularization
- Random forest
- Gradient boosting, if available

Primary evaluation goal:

Improve overall diagnostic discrimination while retaining high recall.

### Validation Strategy

Use a single stratified train/test split with `random_state=42` and `test_size=0.25`, plus 5-fold stratified cross-validation for model selection.

Metrics:

- ROC-AUC
- Precision
- Recall/sensitivity
- Specificity
- F1 score
- Balanced accuracy
- Confusion matrix

Threshold selection (no test-set leakage):

1. Cross-validate the chosen model on the **training** set with `cross_val_predict(method="predict_proba")`.
2. Sweep candidate thresholds against the out-of-fold probabilities, selecting the one that achieves recall ≥ 0.90 while maximising specificity (then precision, then F1).
3. Refit the model on the **full** training set.
4. Touch the held-out test set exactly once for the final metrics report.

Risk tiers ("Low", "Moderate", "High") are anchored to the model's chosen threshold so that a tier label can never contradict the prediction:

- `Low` if `probability < threshold`
- `Moderate` if `threshold <= probability < min(0.90, threshold + 0.20)`
- `High` otherwise

Avoid overclaiming:

- The dataset is from 10 hospitals in Kerala, India and may not generalise globally.
- The model is decision support, not a standalone diagnostic device.
- External validation is needed before clinical deployment.

### Explainability Plan

Explainability is a core feature.

Implemented:

- **Global drivers.** Tree feature importances for ensemble models; standardised log-odds coefficients for logistic regression. Exported to `outputs/metrics/{screening,enhanced}_feature_importance.csv` and plotted to `outputs/figures/`.
- **Patient-level SHAP attributions.** Notebook 05 computes per-feature log-odds contributions for every demo prediction using `shap.TreeExplainer` for tree models and `shap.LinearExplainer` (with a small training-set background) for logistic regression. SHAP values are also surfaced in the Streamlit prototype as a sortable table next to each prediction.
- **Honest demo cases.** Demo patients are pulled from the **test slice** of the train/test split (reproduced from the same seed), so SHAP explanations describe rows the model never trained on.
- **Clinical-domain grouping** is implicit in the feature set (reproductive/menstrual, hyperandrogenic, metabolic, hormonal, ultrasound) and surfaced in the slide deck.

Clinician-facing explanation example:

> Elevated risk is mainly driven by irregular cycles, increased follicle counts, elevated AMH, weight gain, and hirsutism-related symptoms.

### Differential Diagnosis Layer

Use the endometriosis dataset to create a secondary educational or triage module.

Possible implementation:

1. Train a simple endometriosis risk model using the synthetic dataset.
2. Map overlapping features between PCOS and endometriosis:
   - Menstrual irregularity
   - BMI
   - Infertility
   - Hormone abnormality
3. Add chronic pain as a key differential signal.
4. In the prototype, if chronic pain and infertility are high alongside menstrual irregularity, show:

> Symptom overlap detected. Consider differential workup for endometriosis or other gynecologic conditions.

Be clear in slides:

- This is not a validated multi-disease diagnostic model.
- It demonstrates how the system could reduce tunnel vision and prompt broader evaluation.

## Prototype Plan

Implemented as a Streamlit app at [`src/app.py`](src/app.py). Launch with `streamlit run src/app.py` from the project root after running notebooks 02-04 to produce the model artifacts.

### Tab 1: Patient assessment

Patient intake form (collapsible sections):

- Symptoms and basic vitals: age, BMI, cycle pattern/length, weight gain, hair growth, skin darkening, hair loss, pimples, RBS, BP systolic/diastolic.
- Labs and ultrasound (expander): Hb, FSH, LH, TSH, AMH, prolactin, vitamin D3, progesterone, follicle counts and sizes, endometrium thickness. `FSH/LH` is derived automatically.
- Differential workup (expander): menstrual irregularity, chronic pain (0-10), hormone-level abnormality, infertility.

On "Run assessment", the app renders three result blocks stacked vertically:

1. **Frontline screening** - probability, action threshold, threshold-aware risk tier, top 6 SHAP drivers in log-odds units.
2. **Enhanced diagnostic support** - same shape using the labs/ultrasound model.
3. **Endometriosis-overlap prompt** - warning or info note framed as a workflow nudge, with the synthetic-data caveat visible.

### Tab 2: Population view

- Symptom prevalence by PCOS status, read directly from `outputs/metrics/pcos_symptom_rates.csv`.
- Held-out ROC-AUC and recall for both PCOS models.

### Tab 3: About

- Plain-language description of the three models, the threshold strategy, and the data caveats.

## Technology Stack

In use:

- Python 3.12 for data science
- pandas + numpy for data loading and cleaning
- scikit-learn 1.6 for modelling (Logistic Regression, Random Forest, Gradient Boosting, Dummy baseline)
- SHAP 0.51 for per-patient explanations
- matplotlib + seaborn for plots
- Streamlit for the clinician-facing prototype
- joblib for serialising model artifacts
- Node.js (only used by `scripts/create_training_notebooks.mjs` to deterministically regenerate the notebook set)

Repository structure (as built):

```text
biohackathon/
  _read_extract/                  # source datasets (extracted)
  notebooks/
    01_pcos_data_audit_and_eda.ipynb
    02_train_pcos_screening_model.ipynb
    03_train_pcos_enhanced_model.ipynb
    04_train_endometriosis_overlap_model.ipynb
    05_thresholds_explainability_and_demo.ipynb
    06_single_cell_gene_peek.ipynb
    README.md
  outputs/
    figures/                      # plots used in the deck
    metrics/                      # CSV/JSON metric exports + model card
    models/                       # joblib model artifacts
    pcos_cleaned.csv
  scripts/
    create_training_notebooks.mjs # regenerates notebooks deterministically
  src/
    app.py                        # Streamlit prototype
  PROJECT_PLAN.md
  README.md
  requirements.txt
```

The Python data-cleaning, feature, and training logic lives inside the notebook setup cells (generated from the `.mjs` file). This keeps the notebooks self-contained for the judges while still being deterministic to regenerate.

## Presentation Strategy

### Slide 1: Problem

Women experience delayed and missed diagnoses. PCOS is common, heterogeneous, and frequently undiagnosed.

### Slide 2: Why PCOS Is Hard

Show PCOS requires synthesizing symptoms, hormones, metabolic risk, and ultrasound findings.

### Slide 3: Proposed Solution

Introduce PCOS Pathfinder as tiered decision support.

### Slide 4: Data

Show required PCOS dataset and optional endometriosis/single-cell datasets.

### Slide 5: Clinical Feature Map

Group features by clinical domain.

### Slide 6: Modeling Workflow

Raw data -> cleaning -> screening model -> enhanced model -> explanation -> clinician recommendation.

### Slide 7: Results

Show model performance and confusion matrix.

### Slide 8: Explainability

Show top predictors and one example patient explanation.

### Slide 9: Differential Diagnosis

Show endometriosis-overlap warning and why it matters.

### Slide 10: Prototype Demo

Screenshots or live demo.

### Slide 11: Feasibility

Explain clinical workflow:

- Primary care intake
- Risk flag
- Lab/ultrasound prioritization
- Referral support

### Slide 12: Equity and Public Health

Discuss low-resource settings, early detection, and limitations due to missing demographic variables.

### Slide 13: Limitations and Future Work

Mention dataset size, geography, synthetic endometriosis data, need for external validation, and future single-cell biomarker integration.

### Slide 14: Impact

Earlier identification, fewer missed cases, better patient trust, and more efficient referrals.

## Timeline

### May 11, 2026

- Confirm problem framing.
- Read challenge documents and datasets.
- Profile PCOS and endometriosis data.
- Set up project repository structure.
- Create initial EDA notebook.

### May 12-13, 2026

- Clean PCOS dataset.
- Build screening and enhanced feature sets.
- Train baseline models.
- Produce first metrics and plots.
- Attend speaker sessions and use insights to strengthen clinical framing.

### May 14-15, 2026

- Improve modeling pipeline.
- Add cross-validation.
- Add threshold tuning for high recall.
- Add feature importance and patient-level explanations.
- Begin prototype.

### May 16-17, 2026

- Add endometriosis-overlap module.
- Add prototype screens.
- Create initial slide outline.
- Write README and document limitations.

### May 18, 2026

- Polish model outputs.
- Stress-test edge cases.
- Create final figures.
- Prepare demo script.

### May 19, 2026

- Finalize slides.
- Finalize code cleanup.
- Run reproducibility check.
- Package submission files.

### May 20, 2026

- Submit code, slides, and any required self-sourced or processed datasets.

### May 21-22, 2026

- Present demo.
- Emphasize clinical usefulness, explainability, feasibility, and patient impact.

## Risk Register

### Risk: Small PCOS Dataset

Mitigation:

- Use cross-validation.
- Avoid overfitting.
- Prefer interpretable baselines.
- Clearly state need for external validation.

### Risk: Outliers Distort Model

Mitigation:

- Identify and cap or transform extreme values.
- Compare model performance with and without extreme outlier handling.
- Document decisions.

### Risk: Synthetic Endometriosis Dataset

Mitigation:

- Use only for differential-diagnosis demonstration.
- Avoid claiming clinical validation.

### Risk: Single-Cell Analysis Is Too Heavy

Mitigation:

- Keep it as optional biological support.
- Use it for future-work framing unless time permits deeper analysis.

### Risk: Clinical Overclaiming

Mitigation:

- Position as decision support.
- Use language like "risk," "triage," "flag," and "recommend further assessment."
- Do not claim automated diagnosis.

### Risk: Equity Claims Without Demographic Data

Mitigation:

- Discuss equity through workflow design and low-resource feasibility.
- Acknowledge lack of race, income, geography, and access-to-care variables in the dataset.

## Success Criteria

By submission, the project should have:

- A cleaned and documented PCOS dataset pipeline (notebook 01, exported audit + coercion reports). ✓
- Two PCOS models with cross-validated metrics and held-out evaluation (notebooks 02, 03). ✓
- Threshold selection on training-CV out-of-fold probabilities, not the test set. ✓
- Global and patient-level SHAP explanations (notebook 05). ✓
- A differential-diagnosis prompt module using the synthetic endometriosis dataset (notebook 04). ✓
- A single-cell biological-rationale peek (notebook 06). ✓
- **Bootstrap 95% CIs on every held-out metric + paired AUC-difference test** (notebook 07). ✓
- **Calibration (Brier, ECE, Platt, isotonic)** (notebook 08). ✓
- **Decision Curve Analysis with net-benefit useful ranges** (notebook 09). ✓
- **TabPFN-v2 benchmark vs Random Forest** (notebook 10). ✓
- **Subgroup fairness audit by age and BMI with bootstrap CIs** (notebook 11). ✓
- **Split-conformal prediction with empirical-coverage check** (notebook 12). ✓
- **Rotterdam clinical-rule benchmark** (notebook 13). ✓
- A working Streamlit prototype that loads all three model artifacts (`src/app.py`). ✓
- A 15-page technical report PDF with cited recent literature (`report/pcos_pathfinder_report.pdf`). ✓
- A project-root README and an updated PROJECT_PLAN. ✓
- A persuasive slide deck aligned to the judging criteria. (drafted in this plan; deck to follow)

## Methodology Rigor Upgrades

Seven analyses were added on top of the base pipeline to align the submission with TRIPOD+AI 2024 reporting standards and contemporary clinical-ML best practice. Each is independently reproducible from a numbered notebook and is summarised in the technical report (`report/pcos_pathfinder_report.pdf`).

| # | Notebook | Analysis | Recent reference |
|---|---|---|---|
| 07 | `07_uncertainty_quantification.ipynb` | 2000-resample bootstrap 95% CIs on every held-out metric; paired AUC-difference test (enhanced vs screening: ΔAUC=+0.057, 95% CI [+0.013, +0.105], p≈0.015). | Collins et al., *BMJ* 2024 (TRIPOD+AI) |
| 08 | `08_calibration_analysis.ipynb` | Brier, ECE, Platt and isotonic recalibration on a held-out 122-row calibration slice. Enhanced model: Brier 0.093→0.072, ECE 0.143→0.045. | Van Calster et al., *BMC Med* 2019 |
| 09 | `09_decision_curve_analysis.ipynb` | Net-benefit curves vs treat-all / treat-none. Screening useful range [0.020, 0.885]; enhanced [0.010, 0.960]; both action thresholds inside their useful range. | Vickers & Elkin 2006; Vickers et al., *BMJ* 2016 |
| 10 | `10_tabpfn_benchmark.ipynb` | TabPFN-v2 (transformer foundation model for small tabular data) vs Random Forest on the same split, features, and thresholds. TabPFN: screening AUC 0.905, enhanced AUC 0.962 (vs RF 0.896 / 0.953). | Hollmann et al., *Nature* 2025 |
| 11 | `11_subgroup_fairness.ipynb` | Recall stratified by age band and BMI category, with 1000-bootstrap CIs per subgroup. **Honest finding:** 25-point BMI recall gap in screening (lowest in normal-BMI band), narrowing to 20 points in enhanced. | Obermeyer et al., *Science* 2019 |
| 12 | `12_conformal_prediction.ipynb` | Split-conformal prediction sets with distribution-free coverage guarantee. Target 0.90, empirical 0.912 on holdout; mean set size 0.99. | Angelopoulos & Bates, *Found. Trends ML* 2023 |
| 13 | `13_rotterdam_alignment.ipynb` | Hand-coded Rotterdam 2-of-3 clinical rule vs enhanced ML on the same holdout. ML adds 9.1 pts sensitivity for 1.1 pts specificity cost. | Rotterdam 2003; Teede et al., *Fertil Steril* 2023 |

All seven were implemented in parallel git worktrees as part of a single `/batch` orchestration, then integrated on the `feat-integration` branch.

## Final Recommendation

Prioritize a clinically credible, explainable, and feasible decision-support workflow over a complex black-box model. The strongest version of this project will show that the team understands both the biology of PCOS and the real-world diagnostic pathway.

The winning angle is not just "we predicted PCOS." It is:

> We built a tiered, explainable system that helps clinicians identify high-risk patients earlier, choose the next appropriate investigation, and avoid overlooking overlapping women's health conditions.
