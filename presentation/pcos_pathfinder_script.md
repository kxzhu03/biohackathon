# PCOS Pathfinder — 12-Minute Pitch Script

**Target length:** 12 minutes.
**Deck:** [`presentation/pcos_pathfinder_deck.html`](pcos_pathfinder_deck.html).
**Tone:** clinical, practical, evidence-first.

Five of the 18 slides are live-walkthrough demos (code + pre-rendered output) interleaved with the high-level slides they support. They display the actual notebook code on the left and the metric output on the right — no execution required.

## Running order

| # | Slide | Time |
|---|---|---|
| 1 | Title | 0:00-0:30 |
| 2 | Problem | 0:30-1:10 |
| 3 | Workflow | 1:10-1:50 |
| 4 | Data | 1:50-2:30 |
| 5 | Demo 1: Data audit (demo) | 2:30-3:10 |
| 6 | Method | 3:10-3:50 |
| 7 | Demo 2: Threshold CV (demo) | 3:50-4:30 |
| 8 | Results | 4:30-5:10 |
| 9 | Rigor | 5:10-5:45 |
| 10 | Demo 3: Bootstrap CIs (demo) | 5:45-6:25 |
| 11 | Utility | 6:25-7:05 |
| 12 | Demo 5: Conformal (demo) | 7:05-7:45 |
| 13 | Explainability | 7:45-8:20 |
| 14 | Demo 4: Patient SHAP (demo) | 8:20-9:00 |
| 15 | Benchmarks | 9:00-9:40 |
| 16 | Differential | 9:40-10:15 |
| 17 | Implementation | 10:15-11:00 |
| 18 | Impact | 11:00-12:00 |

## Slide 1 — Title (0:00-0:30)

Good morning. We built PCOS Pathfinder: a practical, explainable decision-support workflow for earlier PCOS detection. Our thesis is simple: clinical AI should not just predict a label. It should help clinicians decide who needs assessment, explain why, and avoid missing overlapping conditions. On the held-out split, the enhanced model reaches 0.953 ROC-AUC with 0.886 sensitivity, and everything is reproducible from thirteen notebooks.

## Slide 2 — Problem (0:30-1:10)

The challenge asks us to improve diagnostic accuracy in women's health. PCOS is a perfect core case because it is common, heterogeneous, and often delayed. A patient may first present with acne, hair growth, irregular bleeding, weight changes, or fertility concerns. Those signals are clinically meaningful, but they are often spread across visits and specialists. So our design goal is not just a high AUC. It is a workflow that fits the diagnostic pathway.

## Slide 3 — Workflow (1:10-1:50)

The product is tiered. First, a frontline model uses low-friction data. Second, an enhanced model uses labs and ultrasound. Third, the app shows a diagnostic-completeness checklist so the clinician sees what evidence is present and what is missing. Fourth, the overlap prompt warns when the symptom pattern deserves broader gynecologic workup. That is why this is decision support, not automated diagnosis.

## Slide 4 — Data (1:50-2:30)

The data boundaries are as important as the model. We use the PCOS clinical data as the foundation. The endometriosis dataset is synthetic, so we only use it as a workflow prompt. The single-cell data supports biological rationale only. We also fixed a critical data-quality issue: the source says cycle length, but the range is zero to twelve days, so it is actually bleeding duration. That prevents out-of-distribution inputs like twenty-eight days.

## Slide 5 — Demo 1: Data audit (2:30-3:10) — Live walkthrough

This is the cleaning step. Every column gets numeric-coerced and every non-numeric cell that drops to NaN is recorded with an example. That is how we caught the literal string "1.99." in the second beta-HCG column and the literal letter "a" in the AMH column. We drop identifiers, the blood-group ordinal codes, and the marriage-status column. The marriage-status drop is clinical safety, not just statistics.

## Slide 6 — Method (3:10-3:50)

The key methodological point is that the threshold is not chosen on the test set. We select models using cross-validation on training data, then choose thresholds using out-of-fold probabilities from that training split. Only after that do we evaluate on the held-out test set. That keeps the final metrics honest. We also optimize for recall because this is triage: missing a PCOS case is more costly than sending someone for follow-up.

## Slide 7 — Demo 2: Threshold CV (3:50-4:30) — Live walkthrough

A common failure mode in clinical ML pitches is choosing the threshold on the same test set you then report metrics from. We avoid it. The threshold is picked from out-of-fold training probabilities. The held-out test set is evaluated exactly once, after the model is refit on the full training data. That is why the recall and specificity numbers you see in the results slide are honest.

## Slide 8 — Results (4:30-5:10)

Here is the headline. The screening model catches 39 of 44 PCOS-positive patients in the holdout cohort. The enhanced model keeps the same sensitivity, but raises specificity from 0.685 to 0.902 and precision from 0.574 to 0.812. That is the point of the tiered workflow: screen broadly first, then use labs and ultrasound to reduce false positives.

## Slide 9 — Rigor (5:10-5:45)

Point estimates alone are not enough for a clinical prediction pitch. We added bootstrap confidence intervals, calibration, decision curve analysis, conformal prediction, subgroup audits, TabPFN benchmarking, and a Rotterdam comparison. This lets us say not only that the model performs well, but that we understand uncertainty, probability quality, action thresholds, and failure modes.

## Slide 10 — Demo 3: Bootstrap CIs (5:45-6:25) — Live walkthrough

Point estimates without intervals look like undergraduate work in a clinical-ML paper. So we ran a paired bootstrap: same 2000 resampled index vectors for both models, computed delta-AUC on each, and reported the 2.5 and 97.5 percentile of the differences plus the empirical two-sided p value. The enhanced model is above the screening model on AUC with 95 percent confidence, on this holdout. That is the kind of statement that survives peer review.

## Slide 11 — Utility (6:25-7:05)

Decision curve analysis asks whether a model helps at clinically plausible thresholds. Our selected thresholds do. We also found an honest fairness risk: recall is lower in the normal-BMI group for screening. Rather than hide that, we added a warning to the prototype. The safety point is simple: average performance is not enough if a subgroup can be missed.

## Slide 12 — Demo 5: Conformal (7:05-7:45) — Live walkthrough

The last demo is the modern uncertainty layer. Split-conformal gives each patient a prediction set with a distribution-free coverage guarantee. We hold out 30% of the training set as a calibration slice, compute one minus the model probability of the true label on it, and pick q-hat at the appropriate quantile. The patient's prediction set is every label whose one-minus-probability is at or below q-hat. We targeted 90% coverage and observed 91.2% on the holdout. Empty sets count as abstentions — the model saying it does not know with high confidence.

## Slide 13 — Explainability (7:45-8:20)

Explainability is not an afterthought. The clinician sees the probability, the action threshold, the risk tier, and the top SHAP contributors. In the enhanced model, follicle counts rise to the top, which is clinically sensible. We also add a checklist that translates model output into next-step reasoning: what evidence supports PCOS, what evidence is missing, and what should not be overlooked.

## Slide 14 — Demo 4: Patient SHAP (8:20-9:00) — Live walkthrough

This is the explainability slide that wins clinicians. For one held-out positive case, the model says PCOS. SHAP tells you why: high follicle counts on both ovaries are doing most of the work, with AMH and cycle irregularity contributing, and the absence of skin darkening and weight gain pulling slightly the other way. The patient comes from the test slice, so the explanation describes a row the model never trained on.

## Slide 15 — Benchmarks (9:00-9:40)

We did not stop at comparing random forest to logistic regression. We benchmarked against TabPFN, a modern small-tabular foundation model, and against a Rotterdam-style clinical rule. TabPFN slightly improves AUC, but the random forest keeps better recall and F2 at the selected action threshold and is easier to deploy. Against Rotterdam, enhanced ML catches more positives with only a small specificity cost. We also state the limitation: the dataset lacks testosterone.

## Slide 16 — Differential (9:40-10:15)

The differential module is deliberately framed as a prompt. Because the endometriosis dataset is synthetic, we do not claim clinical diagnostic validity. But it is still useful for the hackathon goal: when chronic pain, infertility, hormonal abnormality, and menstrual irregularity cluster together, the system reminds the clinician not to stop thinking after the PCOS risk score.

## Slide 17 — Implementation (10:15-11:00)

This is feasible because it is already implemented. The Streamlit app loads saved artifacts, the notebooks reproduce the metrics, and the outputs are packaged for review. But we do not pretend this is ready for clinical deployment. The next step is external validation, then a silent pilot, then prospective evaluation. That balance of ambition and restraint is important.

## Slide 18 — Impact (11:00-12:00)

The public-health value is earlier triage. The low-resource value is that the first model does not require labs or ultrasound. The safety value is that the system explains itself and states what it does not know. And the equity value is honesty: we found a subgroup risk and built a warning around it, rather than presenting a polished but unsafe story.

---

## Speaker tips

- The demo slides each have a **takeaway band** in coral at the bottom. If you are short on time on any individual demo, read that one sentence and move on — judges will get the point.
- Press `n` during the deck to show the speaker-notes panel; press `n` again to hide. Arrow keys / spacebar advance.
- The slide footer at the bottom right shows the current slide number and the planned time range, so you can stay on pace at a glance.
- If a judge asks a code-level question during Q&A, navigate to the relevant demo slide by hash (e.g. `#5` for the data-audit demo, `#10` for bootstrap, `#12` for conformal, `#14` for SHAP).
