# PCOS Pathfinder — 9-minute pitch script

**Target length:** 9 minutes presentation + 3 minutes Q&A (per Biohackathon 2026 schedule).
**Deck:** [`presentation/pcos_pathfinder_deck.pptx`](pcos_pathfinder_deck.pptx) — 18 main slides + 5 demo-code appendix.
**Tone:** clinical, practical, evidence-first.

## Running order

| # | Slide | Time |
|---|---|---|
| 1 | Title | 0:00 – 0:25 |
| 2 | Diagnostic gap | 0:25 – 1:00 |
| 3 | Pathophysiology · HPO axis | 1:00 – 1:30 |
| 4 | Pathophysiology · Metabolic axis | 1:30 – 2:00 |
| 5 | Morphology · Follicular arrest | 2:00 – 2:30 |
| 6 | Heterogeneity · Rotterdam phenotypes | 2:30 – 3:00 |
| 7 | Molecular rationale · Single-cell overlap | 3:00 – 3:30 |
| 8 | Tiered workflow | 3:30 – 4:00 |
| 9 | Data foundation | 4:00 – 4:30 |
| 10 | Method & validation | 4:30 – 5:00 |
| 11 | Results | 5:00 – 5:30 |
| 12 | Rigor (TRIPOD+AI) | 5:30 – 6:00 |
| 13 | Clinical utility & subgroup safety | 6:00 – 6:30 |
| 14 | Explainability | 6:30 – 7:00 |
| 15 | External benchmarks | 7:00 – 7:30 |
| 16 | Differential prompt | 7:30 – 8:00 |
| 17 | App walkthrough (high + low) | 8:00 – 8:30 |
| 18 | Implementation & impact | 8:30 – 9:00 |

Slides 19–23 are live-code demo appendix slides (data audit, threshold CV, bootstrap CIs, SHAP, conformal). Reserved for the 3-minute Q&A — navigate by slide number if a judge asks about the code.

## Slide 1 — Title (0:00 – 0:25)

Good morning. We built **PCOS Pathfinder** — a tiered, explainable decision-support workflow for earlier PCOS detection. Held-out enhanced AUC 0.953, sensitivity 0.886, reproducible from thirteen notebooks.

## Slide 2 — The diagnostic gap (0:25 – 1:00)

PCOS affects 8 to 13 percent of reproductive-age women. The average diagnostic delay is over four years, and an estimated 70 percent remain undiagnosed globally (Teede et al., *Fertil Steril* 2023). The problem isn't modelling alone — it's a fragmented diagnostic pathway that misses complex presentations and overlaps with adjacent conditions.

## Slide 3 — Pathophysiology · HPO axis (1:00 – 1:30)

The hyperandrogenism in PCOS is upstream of the ovary. Faster GnRH pulses raise LH relative to FSH, theca cells overproduce androgens, and aromatization to estradiol falls. Our screening tier reads the downstream skin and cycle features; the enhanced tier adds AMH and LH:FSH context.

## Slide 4 — Pathophysiology · Metabolic axis (1:30 – 2:00)

Insulin resistance amplifies the loop: hyperinsulinemia drives theca androgen output and lowers SHBG, raising free testosterone. That's why PCOS confers three- to seven-times the risk of type-two diabetes. Our app warns on lean PCOS because metabolic risk is not purely BMI-driven.

## Slide 5 — Morphology · Follicular arrest (2:00 – 2:30)

Polycystic morphology is follicular arrest, not multiple cysts — twelve or more small antral follicles, arrested at two to nine millimetres, arranged peripherally (Rotterdam 2003 criterion). This is why follicle counts dominate the enhanced-model SHAP for positive cases.

## Slide 6 — Heterogeneity · Rotterdam phenotypes (2:30 – 3:00)

PCOS is four phenotypes, not one disease (Lizneva 2016). Phenotype B can lack ultrasound findings — the screening tier must catch it without follicle counts. Lean PCOS overlaps multiple phenotypes, directly motivating the lean-PCOS warning we measured and surfaced.

## Slide 7 — Molecular rationale · Single-cell overlap (3:00 – 3:30)

We cross-referenced single-cell ovary feature lists with curated PCOS gene programs across steroidogenesis, androgen signalling, insulin axis, follicular development, and GWAS loci. Twenty matches. Biological rationale only — not an expression analysis.

## Slide 8 — Tiered workflow (3:30 – 4:00)

The system is four steps: a frontline screening model on symptoms and vitals, an enhanced model with labs and ultrasound, a Rotterdam-style completeness checklist, and an endometriosis-overlap nudge. We give clinicians a sequence of next-best actions, not an opaque yes/no diagnosis.

## Slide 9 — Data foundation (4:00 – 4:30)

The data is single-source — 541 patients across 10 hospitals in Kerala, India. We caught a data-quality issue the Kaggle docs mislabel: the "cycle length" column is actually bleeding duration (0–12 days). We log every silent coercion, exclude lifestyle proxies that risk stigma, and withhold blood-group ABO codes from the model per Yang et al. 2025.

## Slide 10 — Method & validation (4:30 – 5:00)

Threshold selection avoids test leakage: we pick thresholds from out-of-fold training probabilities targeting recall above 0.90, then evaluate the held-out test set exactly once. We optimize for recall because missing a PCOS case is more costly than sending someone for follow-up.

## Slide 11 — Results (5:00 – 5:30)

On the held-out split, the screening model catches 39 of 44 positives. The enhanced model preserves sensitivity but raises specificity from 0.69 to 0.90 and precision from 0.57 to 0.81. The paired bootstrap test puts the AUC advantage above zero with 95 percent confidence — ΔAUC +0.057, p around 0.015.

## Slide 12 — Rigor · TRIPOD+AI (5:30 – 6:00)

TRIPOD+AI-style reporting (Collins et al., *BMJ* 2024): 2000-resample bootstrap CIs on every metric, Platt-rescaled calibration improving ECE from 0.143 to 0.045, and split-conformal coverage of 0.912 against a 0.90 target. Empty conformal sets count as honest abstentions.

## Slide 13 — Clinical utility & subgroup safety (6:00 – 6:30)

Decision-curve analysis confirms both action thresholds sit inside useful net-benefit ranges. The honest fairness finding: the screening model has a 25-point BMI recall gap, lowest in normal-BMI patients. The app warns clinicians not to rule out lean PCOS solely from a low score.

## Slide 14 — Explainability (6:30 – 7:00)

Every prediction comes with patient-level SHAP attributions plus a Rotterdam-style diagnostic-completeness checklist. The clinician sees which findings pushed the prediction up or down, and which evidence is still missing.

## Slide 15 — External benchmarks (7:00 – 7:30)

We benchmarked against TabPFN-v2, a *Nature* 2025 foundation model for tabular data, and against a hand-coded Rotterdam 2-of-3 rule (Teede 2023). TabPFN trades away recall at our clinical threshold; enhanced ML adds nine sensitivity points over Rotterdam for a 1.1-point specificity cost.

## Slide 16 — Differential prompt (7:30 – 8:00)

The endometriosis module is a synthetic-data nudge, not a diagnostic claim. When chronic pain, infertility, and menstrual irregularity cluster, the system reminds the clinician not to stop thinking after the PCOS score.

## Slide 17 — App walkthrough · two held-out cases (8:00 – 8:30)

Two held-out cases side by side. **The PCOS-positive patient**: follicle counts 10 and 9, irregular cycle, skin darkening — both tiers say High Risk, all four checklist boxes tick, SHAP confirms follicle morphology dominates. **The non-PCOS patient**: elevated AMH at 11.4 might worry a clinician, but low follicle counts and a regular cycle correctly drive a Low Risk score on both tiers.

## Slide 18 — Implementation & impact (8:30 – 9:00)

The deployment path is honest: internal validation, silent pilot, prospective study — external validation before any clinical claim. The impact is earlier triage for delayed patients, a screening tier that needs no labs for low-resource settings, transparent SHAP and conformal abstention for safety, and subgroup gaps we measured and surfaced rather than hid. Thank you.

---

## Speaker tips

- **9 minutes total.** Aim for roughly 30 seconds per slide — the cards carry the headline, so you don't need to read everything.
- **Appendix is your safety net.** If a judge asks about the code in Q&A, the five demo slides (19–23) show actual notebook code with output side by side: data audit (19), threshold CV (20), bootstrap CIs (21), SHAP (22), conformal (23).
- **Arrow keys** advance slides. Slide-number indicator is bottom-right.
- **Two slides to slow down on**: Slide 11 (Results — point to the +21.7 specificity jump and the paired-bootstrap CI excluding zero) and Slide 13 (Subgroup honesty — the 25-point BMI gap is the one finding judges remember).
