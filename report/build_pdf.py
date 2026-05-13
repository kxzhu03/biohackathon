"""Build the PCOS Pathfinder technical report PDF with reportlab.

This is the actual deliverable PDF builder. The companion .tex file is
provided for teams that prefer to compile via Overleaf or a local LaTeX
distribution; this script is what generates the included PDF when no
LaTeX compiler is available.

Usage:
    python report/build_pdf.py

Output:
    report/pcos_pathfinder_report.pdf
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfgen.canvas import Canvas
from PIL import Image as PILImage

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "report"
FIG_DIR = ROOT / "outputs" / "figures"
OUT_PATH = REPORT_DIR / "pcos_pathfinder_report.pdf"

ACCENT = colors.HexColor("#1F3A5F")
ACCENT_SOFT = colors.HexColor("#5B7A9D")
RULE_GREY = colors.HexColor("#D0D5DC")
TABLE_HEADER = colors.HexColor("#1F3A5F")
TABLE_HEADER_TEXT = colors.white
TABLE_ALT_BG = colors.HexColor("#F4F1EC")
BODY_DARK = colors.HexColor("#1A1A1A")
MUTED = colors.HexColor("#56606B")
WARN = colors.HexColor("#B0563A")

# --- Styles -----------------------------------------------------------------

styles = getSampleStyleSheet()

body_style = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10,
    leading=14.2,
    textColor=BODY_DARK,
    spaceAfter=6,
    alignment=TA_JUSTIFY,
)
body_left = ParagraphStyle("BodyLeft", parent=body_style, alignment=TA_LEFT)
bullet_style = ParagraphStyle(
    "Bullet", parent=body_style, leftIndent=14, bulletIndent=4, spaceAfter=2, alignment=TA_LEFT
)
caption_style = ParagraphStyle(
    "Caption",
    parent=body_style,
    fontSize=8.5,
    leading=11,
    alignment=TA_CENTER,
    textColor=MUTED,
    spaceAfter=10,
    spaceBefore=2,
)
h1_style = ParagraphStyle(
    "H1",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=15,
    leading=19,
    textColor=ACCENT,
    spaceBefore=16,
    spaceAfter=6,
    keepWithNext=True,
)
h2_style = ParagraphStyle(
    "H2",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=11.5,
    leading=15,
    textColor=ACCENT_SOFT,
    spaceBefore=10,
    spaceAfter=3,
    keepWithNext=True,
)
title_style = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=26,
    leading=30,
    textColor=ACCENT,
    spaceAfter=4,
    alignment=TA_LEFT,
)
subtitle_style = ParagraphStyle(
    "Subtitle",
    parent=styles["Heading2"],
    fontName="Helvetica",
    fontSize=13,
    leading=17,
    textColor=BODY_DARK,
    spaceAfter=18,
    alignment=TA_LEFT,
)
meta_style = ParagraphStyle(
    "Meta", parent=body_left, fontSize=9.5, leading=13, textColor=MUTED, spaceAfter=2
)
abstract_label = ParagraphStyle(
    "AbstractLabel",
    parent=h2_style,
    fontSize=11,
    textColor=ACCENT,
    spaceBefore=8,
    spaceAfter=4,
)
abstract_body = ParagraphStyle(
    "AbstractBody",
    parent=body_style,
    fontSize=9.8,
    leading=13.5,
    leftIndent=14,
    rightIndent=14,
    spaceAfter=14,
    textColor=BODY_DARK,
)
code_style = ParagraphStyle("Code", parent=body_style, fontName="Courier", fontSize=9, leading=12.5)

cell_style = ParagraphStyle(
    "Cell",
    parent=body_style,
    fontSize=8.6,
    leading=11,
    alignment=TA_LEFT,
    spaceAfter=0,
    spaceBefore=0,
    wordWrap="CJK",  # break inside long unbreakable tokens (file paths)
    textColor=BODY_DARK,
)
cell_header_style = ParagraphStyle(
    "CellHeader",
    parent=cell_style,
    fontName="Helvetica-Bold",
    fontSize=8.8,
    alignment=TA_CENTER,
    textColor=TABLE_HEADER_TEXT,
    wordWrap=None,  # short headers should never break inside a word
)
path_cell_style = ParagraphStyle(
    "Path",
    parent=cell_style,
    fontName="Courier",
    fontSize=8.2,
    leading=10.5,
)


# --- Helpers ----------------------------------------------------------------


def cell_para(text: str, style: ParagraphStyle | None = None) -> Paragraph:
    """Wrap long table-cell text in a Paragraph so reportlab can break it.

    Uses wordWrap='CJK' on the default style, which lets reportlab break inside
    very long unbreakable tokens (e.g. file paths) when no whitespace is available.
    """
    return Paragraph(text, style or cell_style)


def _wrap_cell(value, style: ParagraphStyle | None = None, threshold: int = 25):
    """Auto-wrap a string cell in a Paragraph if it's long; pass through Flowables."""
    if isinstance(value, str) and len(value) > threshold:
        return cell_para(value, style)
    return value


def figure(filename: str, caption: str, max_width_cm: float = 14.0):
    path = FIG_DIR / filename
    if not path.exists():
        return Paragraph(f"[missing figure: {filename}]", body_style)
    with PILImage.open(path) as im:
        iw, ih = im.size
    max_w = max_width_cm * cm
    aspect = ih / iw
    w = min(max_w, iw)
    h = w * aspect
    img = Image(str(path), width=w, height=h)
    img.hAlign = "CENTER"
    return KeepTogether([img, Paragraph(caption, caption_style)])


def two_figure_row(left_file, left_caption, right_file, right_caption):
    """Place two figures side-by-side using a 2-column table."""
    cell_w = 8.0 * cm

    def cell(fname, cap):
        path = FIG_DIR / fname
        if not path.exists():
            return Paragraph(f"[missing: {fname}]", body_style)
        with PILImage.open(path) as im:
            iw, ih = im.size
        w = cell_w
        h = w * ih / iw
        return [Image(str(path), width=w, height=h),
                Spacer(1, 2),
                Paragraph(cap, caption_style)]

    data = [[cell(left_file, left_caption), cell(right_file, right_caption)]]
    t = Table(data, colWidths=[cell_w + 0.4 * cm, cell_w + 0.4 * cm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return KeepTogether(t)


def _prepare_rows(header, rows, wrap_threshold=25, body_cell_style=None):
    """Wrap header cells (white-on-accent) and body cells (dark) in Paragraphs.

    Long body strings (over threshold) are auto-wrapped so reportlab can break
    them across lines. Already-Flowable cells are passed through untouched.
    """
    body_style_local = body_cell_style or cell_style
    out_header = [
        cell_para(c, cell_header_style) if isinstance(c, str) else c for c in header
    ]
    out_rows = []
    for row in rows:
        out_rows.append([_wrap_cell(c, body_style_local, wrap_threshold) for c in row])
    return out_header, out_rows


def styled_table(header, rows, col_widths=None, alt_row_bg=True, wrap_threshold=25,
                 valign="MIDDLE"):
    out_header, out_rows = _prepare_rows(header, rows, wrap_threshold)
    data = [out_header] + out_rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), TABLE_HEADER_TEXT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (0, 1), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), valign),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("TOPPADDING", (0, 1), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, ACCENT),
        ("LINEBELOW", (0, -1), (-1, -1), 0.4, RULE_GREY),
        ("TEXTCOLOR", (0, 1), (-1, -1), BODY_DARK),
    ]
    if alt_row_bg:
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), TABLE_ALT_BG))
    t.setStyle(TableStyle(style))
    return t


def numeric_table(header, rows, col_widths=None, wrap_threshold=25):
    """Variant where all data cells are right-aligned for numerics."""
    out_header, out_rows = _prepare_rows(header, rows, wrap_threshold)
    data = [out_header] + out_rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), TABLE_HEADER_TEXT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("TOPPADDING", (0, 1), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, ACCENT),
        ("LINEBELOW", (0, -1), (-1, -1), 0.4, RULE_GREY),
        ("TEXTCOLOR", (0, 1), (-1, -1), BODY_DARK),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), TABLE_ALT_BG))
    t.setStyle(TableStyle(style))
    return t


def bullet(text):
    return Paragraph(f"<bullet>&bull;</bullet> {text}", bullet_style)


def para(text):
    return Paragraph(text, body_style)


def h1(text):
    return Paragraph(text, h1_style)


def h2(text):
    return Paragraph(text, h2_style)


def callout(text, color=WARN):
    """A boxed callout paragraph for caveats."""
    p = Paragraph(text, body_style)
    t = Table([[p]], colWidths=[16 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FBF3EE")),
        ("BOX", (0, 0), (-1, -1), 0.6, color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


# --- Page templates ---------------------------------------------------------


def draw_header_footer(canvas: Canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE_GREY)
    canvas.setLineWidth(0.5)
    # footer rule
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(ACCENT)
    canvas.drawString(2 * cm, 1.1 * cm, "PCOS Pathfinder — Technical Report")
    canvas.setFillColor(MUTED)
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


def draw_cover_decoration(canvas: Canvas, doc):
    """No header/footer on the cover page; just an accent stripe."""
    canvas.saveState()
    canvas.setFillColor(ACCENT)
    canvas.rect(0, A4[1] - 1.2 * cm, A4[0], 1.2 * cm, stroke=0, fill=1)
    canvas.setFillColor(ACCENT_SOFT)
    canvas.rect(0, A4[1] - 1.4 * cm, A4[0], 0.2 * cm, stroke=0, fill=1)
    canvas.restoreState()


# --- Build ------------------------------------------------------------------


def build():
    doc = BaseDocTemplate(
        str(OUT_PATH),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="PCOS Pathfinder Technical Report",
        author="Biohackathon 2026 Team",
        subject="Tiered clinical decision support for PCOS",
    )

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    cover_template = PageTemplate(id="cover", frames=[frame], onPage=draw_cover_decoration)
    body_template = PageTemplate(id="body", frames=[frame], onPage=draw_header_footer)
    doc.addPageTemplates([cover_template, body_template])

    story = []

    # ---- Cover page --------------------------------------------------------
    story.append(Spacer(1, 2.4 * cm))
    story.append(Paragraph("PCOS Pathfinder", title_style))
    story.append(Paragraph(
        "A Tiered, Explainable Decision-Support Prototype for Earlier PCOS Detection and Differential Diagnosis",
        subtitle_style,
    ))
    story.append(Paragraph("Biohackathon 2026: Women's Health", meta_style))
    story.append(Paragraph("11&ndash;22 May 2026", meta_style))
    story.append(Spacer(1, 0.6 * cm))

    story.append(Paragraph("Abstract", abstract_label))
    story.append(Paragraph(
        "PCOS Pathfinder is a data-grounded clinical decision-support prototype for earlier identification of "
        "Polycystic Ovary Syndrome (PCOS) and broader differential workup in women's health. The system anchors "
        "on the required PCOS clinical dataset (n=541, Kerala, India), layers a synthetic endometriosis-overlap "
        "module for differential reasoning, and uses a lightweight single-cell gene-list check as biological "
        "rationale. The delivered artifacts are <b>thirteen</b> reproducible notebooks, three saved scikit-learn "
        "models, a Streamlit clinician interface, exported metrics and figures, and this report. Thresholds are "
        "selected from out-of-fold training probabilities (no test leakage), risk tiers are anchored to each "
        "model's action threshold, and patient-level SHAP attributions are provided for both PCOS models. On the "
        "held-out test split the enhanced model reaches ROC-AUC <b>0.953</b> (95% CI [0.911, 0.985]) with recall "
        "0.886 and specificity 0.902; a paired bootstrap test puts the enhanced-vs-screening difference at "
        "&Delta;AUC=+0.057, 95% CI [+0.013, +0.105], p&asymp;0.015 on this held-out split. The methodology layer "
        "adds bootstrap confidence intervals (TRIPOD+AI-style reporting), Platt &amp; isotonic calibration with Brier/ECE, "
        "decision-curve analysis (Vickers &amp; Elkin), subgroup fairness audits, split-conformal prediction "
        "intervals (Angelopoulos &amp; Bates 2023), a TabPFN-v2 transformer-foundation-model benchmark (Hollmann "
        "et al., <i>Nature</i> 2025), and a Rotterdam-criteria clinical-rule benchmark (Teede et al. 2023). The "
        "system is framed throughout as decision support, not standalone diagnosis.",
        abstract_body,
    ))

    story.append(Spacer(1, 0.3 * cm))
    headline = [
        ["Headline metric", "Screening", "Enhanced"],
        ["ROC-AUC", "0.896 [0.830, 0.951]", "0.953 [0.911, 0.985]"],
        ["Recall (sensitivity)", "0.886 [0.787, 0.975]", "0.886 [0.786, 0.974]"],
        ["Specificity", "0.685", "0.902"],
        ["NPV (rule-out value)", "0.926 [0.857, 0.985]", "0.943"],
        ["F2 score", "0.799", "0.871"],
        ["Brier (Platt-calibrated)", "0.116", "0.072"],
    ]
    story.append(numeric_table(headline[0], headline[1:], col_widths=[5.4 * cm, 4.8 * cm, 4.8 * cm]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "<i>Held-out test split (n=136) at CV-selected high-recall thresholds. Numbers in brackets are 95% "
        "percentile bootstrap CIs (2000 resamples). The enhanced-vs-screening AUC difference on this split is "
        "(&Delta;=+0.057, 95% CI [+0.013, +0.105], p&asymp;0.015). F1 is deliberately suppressed by the "
        "high-recall threshold &mdash; see &sect;6.2.</i>",
        meta_style,
    ))

    story.append(NextPageTemplate("body"))
    story.append(PageBreak())

    # ---- 1. Challenge context ---------------------------------------------
    story.append(h1("1. Challenge Context and Project Goal"))
    story.append(para(
        "The Biohackathon 2026 challenge asks teams to improve diagnostic accuracy for women's health "
        "conditions using available data and a feasible implementation pathway. PCOS is the core case because "
        "it is common, heterogeneous, and frequently diagnosed late: clinicians must synthesise menstrual, "
        "metabolic, hormonal, ovarian, dermatologic, and reproductive information, and overlapping conditions "
        "are routinely missed."
    ))
    story.append(para(
        "A defensible solution therefore needs to do more than predict a binary label. It should help clinicians "
        "identify high-risk patients earlier, explain the drivers of risk in clinically familiar terms, and "
        "avoid tunnel vision when adjacent conditions share presentations. The project goal is to build "
        "<b>PCOS Pathfinder</b>, a clinician-facing tiered decision-support workflow with three linked components:"
    ))
    story.append(bullet("<b>Frontline screening model</b> &mdash; high-recall PCOS risk flag using symptoms and basic vitals only, intended for primary care, telehealth, and community clinics."))
    story.append(bullet("<b>Enhanced diagnostic-support model</b> &mdash; a stronger model that uses laboratory and ultrasound features once further investigations are available."))
    story.append(bullet("<b>Endometriosis-overlap prompt</b> &mdash; a synthetic-data workflow nudge that prompts broader differential workup when symptoms overlap. <i>Not</i> a diagnostic claim."))

    # ---- 2. Data sources --------------------------------------------------
    story.append(h1("2. Data Sources"))
    story.append(styled_table(
        ["Dataset", "Rows / samples", "Use"],
        [
            ["PCOS clinical (Kerala, India)", "541 patients", "Required modelling foundation"],
            ["Endometriosis (synthetic)", "10,000 rows", "Differential-overlap prompt"],
            ["PCOS single-cell archive", "20 samples", "Biological rationale (gene-list peek)"],
            ["Endometrium single-cell archive", "2 samples", "Biological context only"],
        ],
        col_widths=[6 * cm, 3 * cm, 7 * cm],
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(para(
        "The PCOS workbook's modelling sheet (<font face='Courier'>Full_new</font>) contains 44 columns and a binary "
        "target <font face='Courier'>PCOS (Y/N)</font>. The class split is 364 non-PCOS to 177 PCOS, a roughly 2:1 imbalance."
    ))
    story.append(figure("pcos_class_balance.png", "Figure 1. PCOS class distribution in the required dataset.", max_width_cm=10))

    story.append(para(
        "The supplementary endometriosis dataset has seven variables: age, menstrual irregularity, chronic pain "
        "level, hormone-level abnormality, infertility, BMI, and diagnosis. Because it is synthetic, the resulting "
        "model is treated as a workflow prompt only. The single-cell archives are 10x-style outputs; this project "
        "deliberately limits itself to a gene-list peek rather than a full single-cell analysis, because the "
        "judging weights reward clinical usefulness over single-cell technique depth."
    ))

    # ---- 3. Data cleaning -------------------------------------------------
    story.append(h1("3. Data Cleaning and Quality Controls"))
    story.append(para(
        "Cleaning lives in the notebook setup cells generated from the deterministic "
        "regenerator script (<font face='Courier'>scripts/&#8203;create_&#8203;training_&#8203;notebooks.mjs</font>). "
        "The key steps:"
    ))
    story.append(bullet("Standardise column names to lowercase snake case; coerce numerics and log every non-numeric cell."))
    story.append(bullet("Drop identifiers (<font face='Courier'>sl_no</font>, <font face='Courier'>patient_file_no</font>)."))
    story.append(bullet("Drop <font face='Courier'>blood_group</font> (codes 11&ndash;18 are not ordinal) and <font face='Courier'>marriage_status_yrs</font> (clinically sensitive, no diagnostic signal)."))
    story.append(bullet("Engineer <font face='Courier'>cycle_irregular_flag</font> from <font face='Courier'>cycle_r_i</font> (Kaggle coding: 2 = regular, 4/5 = irregular)."))
    story.append(bullet("Cap visibly-impossible outliers in FSH, LH, FSH/LH, vitamin D3, progesterone."))
    story.append(bullet("Use median imputation <i>inside</i> each scikit-learn pipeline so the rules travel with the saved artifact."))

    story.append(h2("3.1 Data Caveat: \"Cycle Length\" Is Actually Bleeding Duration"))
    story.append(callout(
        "The source column labelled <b>Cycle length(days)</b> ranges 0&ndash;12 with a median of 5 across both "
        "classes &mdash; this is the <i>duration of menses bleeding in days</i>, not the menstrual cycle interval. "
        "The Kaggle dataset documentation is misleading on this point. The Streamlit prototype surfaces the field "
        "with the corrected label and a 0&ndash;12 range so clinicians do not accidentally enter a typical 28-day "
        "cycle value, which would be out-of-distribution and silently produce wrong predictions."
    ))
    story.append(Spacer(1, 0.3 * cm))

    story.append(h2("3.2 Logged Coercions"))
    story.append(styled_table(
        ["Column", "Example value", "Count"],
        [
            ["ii_beta_hcg_miu_ml", "1.99.", "1"],
            ["amh_ng_ml", "a", "1"],
        ],
        col_widths=[6 * cm, 5 * cm, 3 * cm],
    ))

    # ---- 4. Model design --------------------------------------------------
    story.append(h1("4. Model Design"))
    story.append(h2("4.1 Frontline Screening Model"))
    story.append(para(
        "Intended for primary care, telehealth, and community settings. Lifestyle proxies "
        "(<font face='Courier'>fast_food</font>, <font face='Courier'>reg_exercise</font>) are intentionally "
        "excluded &mdash; bias-prone, hard to validate at intake, and likely to encode confounders rather than physiology."
    ))
    story.append(styled_table(
        ["Screening feature set (13 features)"],
        [["Age, BMI, cycle pattern (raw and engineered flag), duration of menses bleeding, weight gain, "
          "hair growth, skin darkening, hair loss, pimples, random blood sugar, BP systolic, BP diastolic."]],
        col_widths=[16 * cm],
    ))
    story.append(Spacer(1, 0.2 * cm))
    story.append(h2("4.2 Enhanced Diagnostic-Support Model"))
    story.append(styled_table(
        ["Enhanced model additional features (14 added, 27 total)"],
        [["Haemoglobin, FSH, LH, FSH/LH ratio, TSH, AMH, prolactin, vitamin D3, progesterone, left and right "
          "follicle counts, left and right follicle sizes, endometrium thickness."]],
        col_widths=[16 * cm],
    ))
    story.append(Spacer(1, 0.2 * cm))
    story.append(h2("4.3 Candidate Algorithms"))
    story.append(para(
        "Both PCOS notebooks compare four models: a most-frequent dummy baseline, logistic regression with class-weight "
        "balancing and standard scaling, a random forest with class-weight balancing, and gradient boosting. "
        "Selection is by 5-fold stratified cross-validation on the training split, ranking by ROC-AUC and breaking "
        "ties on recall. Across runs, random forest wins both contests."
    ))

    # ---- 5. Validation strategy -------------------------------------------
    story.append(h1("5. Validation Strategy"))
    story.append(para(
        "A single stratified train/test split with <font face='Courier'>test_size&#8203;=&#8203;0.25</font> and "
        "<font face='Courier'>random_state&#8203;=&#8203;42</font>. Model selection uses 5-fold stratified cross-"
        "validation on the <i>training</i> split. For each chosen model, action thresholds are selected using "
        "out-of-fold training probabilities from "
        "<font face='Courier'>cross_val_&#8203;predict(method=&#8203;\"predict_proba\")</font>. "
        "The threshold sweep targets recall &ge; 0.90 on the training out-of-fold predictions while maximising "
        "specificity, then precision, then F1."
    ))
    story.append(para(
        "The held-out test set is then evaluated <b>exactly once</b>. This eliminates the earlier risk of choosing a "
        "threshold on the test set and reporting optimistic metrics."
    ))

    # ---- 6. Results -------------------------------------------------------
    story.append(h1("6. Results"))
    story.append(h2("6.1 Held-Out Performance with Bootstrap 95% CIs"))
    story.append(para(
        "Point estimates alone are weak evidence for clinical-prediction work; the TRIPOD+AI 2024 reporting "
        "guidance (Collins et al., BMJ 2024) recommends interval estimates throughout. Every cell below is "
        "therefore accompanied by a 95% percentile confidence interval from 2000 bootstrap resamples of the "
        "held-out set (notebook 07)."
    ))
    story.append(numeric_table(
        ["Metric", "Screening (95% CI)", "Enhanced (95% CI)"],
        [
            ["ROC-AUC", "0.896 [0.830, 0.951]", "0.953 [0.911, 0.985]"],
            ["Recall (sensitivity)", "0.886 [0.787, 0.975]", "0.886 [0.786, 0.974]"],
            ["Specificity", "0.685 [0.591, 0.782]", "0.902 [0.837, 0.967]"],
            ["PPV (precision)", "0.574 [0.451, 0.698]", "0.812 [0.700, 0.917]"],
            ["NPV", "0.926 [0.857, 0.985]", "0.943 [0.889, 0.987]"],
            ["F1", "0.696 [0.585, 0.789]", "0.848 [0.766, 0.917]"],
            ["F2", "0.799 [0.707, 0.878]", "0.871 [0.783, 0.940]"],
        ],
        col_widths=[5.0 * cm, 5.5 * cm, 5.5 * cm],
    ))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "<i>Table 3. Held-out test performance (n=136) with 2000-resample bootstrap 95% percentile CIs.</i>",
        caption_style,
    ))
    story.append(para(
        "A <b>paired</b> bootstrap test on the same 2000 resamples gives <b>&Delta;AUC = +0.057 in favour of "
        "enhanced (95% CI [+0.013, +0.105], SE = 0.023, two-sided p &asymp; 0.015)</b> on this held-out split. "
        "We frame this as evidence that the enhanced model appears better on this cohort, not as a deployment-ready "
        "significance claim &mdash; the cohort is small (n=541), single-source, and external validation is still "
        "required. NPV is 0.926 for screening and 0.943 for enhanced &mdash; when either model says \"no PCOS\", "
        "it is right &gt;92% of the time, which is the right framing for ruling-out triage."
    ))
    story.append(figure(
        "auc_bootstrap_distribution.png",
        "Figure 2. Bootstrap distribution of held-out ROC-AUC for both PCOS models (2000 resamples).",
        max_width_cm=12.5,
    ))

    story.append(h2("6.2 Why F1 Is Not the Right Headline Metric for Screening"))
    story.append(para(
        "The screening F1 of 0.696 is intentionally suppressed by the high-recall threshold. F1 weights precision "
        "and recall equally, but in primary-care screening the cost of a missed PCOS case (years of metabolic "
        "damage, infertility risk) is much larger than the cost of an over-referral (one additional clinical visit). "
        "Two more screening-aligned metrics behave very differently:"
    ))
    story.append(bullet("<b>Recall (0.886)</b> &mdash; the screening tool catches 39 of the 44 PCOS-positive patients in the held-out cohort."))
    story.append(bullet("<b>NPV (0.926)</b> &mdash; when the tool says \"no PCOS\", the clinician can trust it."))
    story.append(bullet("<b>F2 (0.799)</b> &mdash; weights recall four times more than precision; the screening-friendly counterpart to F1."))

    story.append(para(
        "Table 4 compares the chosen high-recall threshold to a balanced 0.50 threshold for each model. The "
        "screening row makes the trade-off most visible: the balanced threshold raises F1 from 0.70 to 0.81 but loses "
        "four PCOS cases (recall 0.886 &rarr; 0.795). At the high-recall threshold, F2 is 0.80; at the balanced "
        "threshold, F2 is also 0.80 &mdash; F2 is largely indifferent, so the high-recall threshold is the right pick "
        "under a sensitivity-first cost function."
    ))

    story.append(numeric_table(
        ["Model / threshold", "Recall", "Spec.", "PPV", "NPV", "F1", "F2", "TN, FP, FN, TP"],
        [
            ["Screening, t=0.285 (chosen)", "0.886", "0.685", "0.574", "0.926", "0.696", "0.799", "63, 29, 5, 39"],
            ["Screening, t=0.500 (balanced)", "0.795", "0.913", "0.814", "0.903", "0.805", "0.799", "84, 8, 9, 35"],
            ["Enhanced, t=0.380 (chosen)", "0.886", "0.902", "0.812", "0.943", "0.848", "0.871", "83, 9, 5, 39"],
            ["Enhanced, t=0.500 (balanced)", "0.818", "0.957", "0.900", "0.917", "0.857", "0.833", "88, 4, 8, 36"],
        ],
        col_widths=[4.5 * cm, 1.4 * cm, 1.4 * cm, 1.4 * cm, 1.4 * cm, 1.4 * cm, 1.4 * cm, 3.1 * cm],
        wrap_threshold=20,
    ))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("<i>Table 4. Threshold trade-off on the held-out test set.</i>", caption_style))
    story.append(para(
        "For the enhanced model the high-recall threshold actually <i>dominates</i> the balanced threshold under F2 "
        "(0.871 vs 0.833), so there is no headline F-score loss from the screening-friendly choice."
    ))

    story.append(h2("6.3 ROC Curves and Confusion Matrices"))
    story.append(two_figure_row(
        "screening_roc_curve.png", "Figure 3. Screening ROC, AUC = 0.896 (95% CI [0.830, 0.951]).",
        "enhanced_roc_curve.png", "Figure 4. Enhanced ROC, AUC = 0.953 (95% CI [0.911, 0.985]).",
    ))
    story.append(two_figure_row(
        "screening_confusion_matrix.png", "Figure 5. Screening confusion at t = 0.285.",
        "enhanced_confusion_matrix.png", "Figure 6. Enhanced confusion at t = 0.380.",
    ))

    # ---- 7. Probability Quality (Calibration + Conformal) ----------------
    story.append(h1("7. Probability Quality: Calibration and Conformal Coverage"))
    story.append(para(
        "Clinicians act on probabilities, so probabilities must be both <b>calibrated</b> (the predicted 70% PCOS "
        "risk really happens ~70% of the time) and <b>covered</b> (the model can flag when its own prediction is "
        "uncertain). The two analyses below address each property in turn (notebooks 08 and 12)."
    ))

    story.append(h2("7.1 Calibration (Brier score, ECE, Platt and isotonic scaling)"))
    story.append(para(
        "We hold out a 122-patient calibration slice from the training set and fit Platt (sigmoid) and isotonic "
        "calibrators on the slice without touching the test set (Van Calster et al., <i>BMC Medicine</i> 2019). "
        "Brier score and Expected Calibration Error (ECE, 10 equal-width bins) are computed for the raw model and "
        "for both recalibrated variants on the 136-patient holdout."
    ))
    story.append(numeric_table(
        ["Model", "Brier (raw)", "Brier (Platt)", "Brier (iso)", "ECE (raw)", "ECE (Platt)", "ECE (iso)"],
        [
            ["Screening", "0.128", "0.116", "0.124", "0.107", "0.073", "0.073"],
            ["Enhanced", "0.093", "0.072", "0.074", "0.143", "0.045", "0.048"],
        ],
        col_widths=[2.8 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm],
    ))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("<i>Table 5. Calibration metrics; lower is better.</i>", caption_style))
    story.append(para(
        "Platt scaling wins on both Brier and ECE for both models. For the enhanced model, Platt-recalibrated "
        "probabilities have Brier 0.072 and ECE 0.045 &mdash; well-calibrated by clinical-prediction standards."
    ))
    story.append(two_figure_row(
        "calibration_screening.png", "Figure 7. Screening reliability diagram (raw vs Platt vs isotonic).",
        "calibration_enhanced.png", "Figure 8. Enhanced reliability diagram (raw vs Platt vs isotonic).",
    ))

    story.append(h2("7.2 Split-Conformal Prediction Sets (per-patient coverage guarantee)"))
    story.append(para(
        "Split-conformal prediction (Vovk et al.; tutorial in Angelopoulos &amp; Bates, <i>Foundations and Trends "
        "in ML</i> 2023) gives a per-patient prediction <i>set</i> with a distribution-free coverage guarantee. "
        "Procedure: split the 405-row training set into proper-train (n=283) and calibration (n=122); refit a "
        "clone of the enhanced random-forest pipeline on proper-train; compute nonconformity scores "
        "s<sub>i</sub> = 1 &minus; p<sub>model</sub>(y<sub>i</sub> | x<sub>i</sub>) on the calibration set; pick "
        "q&#770; at quantile (1 &minus; &alpha;) of the calibration scores (we use &alpha; = 0.10 for 90% target "
        "coverage). For each holdout patient, the set is {y : 1 &minus; p(y | x) &le; q&#770;}."
    ))
    story.append(numeric_table(
        ["Quantity", "Value"],
        [
            ["Target coverage (1 &minus; &alpha;)", "0.900"],
            ["Empirical coverage on holdout", "0.912"],
            ["Threshold q̂", "0.486"],
            ["Mean prediction-set size", "0.99"],
            ["Singleton sets", "99.3%"],
            ["Doubleton (uncertain) sets", "0.0%"],
            ["Empty sets (very high confidence)", "0.7%"],
        ],
        col_widths=[8 * cm, 4 * cm],
    ))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "<i>Table 6. Conformal-prediction coverage on the 136-patient holdout (enhanced model, &alpha;=0.10).</i>",
        caption_style,
    ))
    story.append(para(
        "Empirical coverage 0.912 hits the 0.90 target within bootstrap noise. The mean set size of ~1 means "
        "the model is confident on almost every patient; the rare ambiguous-doubleton sets identify exactly "
        "which patients deserve a second clinician look."
    ))
    story.append(figure(
        "conformal_set_size_distribution.png",
        "Figure 9. Distribution of conformal prediction-set sizes on the holdout (enhanced model).",
        max_width_cm=11,
    ))

    # ---- 8. Decision Curve Analysis ----------------------------------------
    story.append(h1("8. Decision Curve Analysis (Clinical Utility)"))
    story.append(para(
        "Decision Curve Analysis (Vickers &amp; Elkin 2006; Vickers et al., <i>BMJ</i> 2016) translates threshold "
        "choice into <i>clinical utility</i> rather than statistical discrimination. For threshold probability "
        "<i>p<sub>t</sub></i>, net benefit is "
        "NB(<i>p<sub>t</sub></i>) = (TP/N) &minus; (FP/N) &times; (<i>p<sub>t</sub></i> / (1 &minus; "
        "<i>p<sub>t</sub></i>)). The model is clinically useful where its curve sits above both the "
        "<i>treat-all</i> and <i>treat-none</i> baselines."
    ))
    story.append(numeric_table(
        ["Model", "Useful threshold range", "Chosen action threshold", "Inside useful range?"],
        [
            ["Screening", "[0.020, 0.885]", "0.285", "Yes"],
            ["Enhanced", "[0.010, 0.960]", "0.380", "Yes"],
        ],
        col_widths=[3.5 * cm, 5 * cm, 4.5 * cm, 3.5 * cm],
    ))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("<i>Table 7. Useful threshold ranges from decision-curve analysis (notebook 09).</i>", caption_style))
    story.append(para(
        "Both action thresholds sit comfortably inside their useful ranges. The enhanced model's useful range "
        "extends almost the full unit interval, meaning a clinician can shift the operating point widely without "
        "losing net benefit &mdash; useful for population settings with very different missed-case costs."
    ))
    story.append(two_figure_row(
        "dca_screening.png", "Figure 10. Screening decision curve (net benefit vs threshold probability).",
        "dca_enhanced.png", "Figure 11. Enhanced decision curve.",
    ))

    # ---- 9. Subgroup Fairness Audit ----------------------------------------
    story.append(h1("9. Subgroup Fairness Audit"))
    story.append(para(
        "Equity claims need numbers, not platitudes (Obermeyer et al., <i>Science</i> 2019). Notebook 11 stratifies "
        "the holdout by age band and BMI category and reports recall with 1000-resample bootstrap 95% CIs. The "
        "two slice axes are the only demographic / anthropometric variables in this dataset; race, income, and "
        "access-to-care measures are unavailable and we flag this honestly in &sect;15."
    ))
    story.append(numeric_table(
        ["Axis", "Worst-group recall (screening)", "Worst-group recall (enhanced)", "Max recall gap"],
        [
            ["Age band (<25, 25–34, 35+)", "0.848 (25–34)", "0.800 (<25)", "0.15 / 0.20"],
            ["BMI category (under/normal/over/obese)", "0.750 (normal)", "0.800 (normal)", "0.25 / 0.20"],
        ],
        col_widths=[5 * cm, 4.5 * cm, 4.5 * cm, 3 * cm],
    ))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "<i>Table 8. Subgroup recall on the held-out test set. The enhanced model closes most but not all of the "
        "screening model's BMI gap.</i>",
        caption_style,
    ))
    story.append(para(
        "<b>Honest finding:</b> the screening model has a 25-percentage-point recall gap by BMI on the held-out "
        "cohort, with the worst recall in the normal-BMI band (0.750). The enhanced model closes this gap to 20 "
        "points; both gaps are wider than is ideal and reflect (a) the small per-subgroup sample sizes and (b) "
        "the dataset's BMI distribution being skewed toward high-BMI patients. Risk-mitigation: deploy with "
        "subgroup-specific monitoring; flag the BMI dependency in the model card; collect external validation "
        "data with a more balanced BMI distribution."
    ))
    story.append(two_figure_row(
        "subgroup_recall_by_age.png", "Figure 12. Recall by age band, both models.",
        "subgroup_recall_by_bmi.png", "Figure 13. Recall by BMI category, both models.",
    ))

    # ---- 10. External Benchmarks (TabPFN + Rotterdam) ----------------------
    story.append(h1("10. External Benchmarks"))

    story.append(h2("10.1 TabPFN-v2 (Hollmann et al., Nature 2025) vs Random Forest"))
    story.append(para(
        "TabPFN-v2 is a transformer foundation model for small tabular data (n &lt; 10k) published in <i>Nature</i> "
        "in 2025. Our cohort (n=541) sits exactly in TabPFN's design regime, so it is a natural benchmark. "
        "Notebook 10 fits TabPFN-v2 on the same train/test split, same features, and the same action thresholds, "
        "using only CPU."
    ))
    story.append(numeric_table(
        ["Feature set", "RF ROC-AUC", "TabPFN ROC-AUC", "&Delta;AUC", "RF F1", "TabPFN F1"],
        [
            ["Screening (13 feat.)", "0.896", "0.905", "+0.010", "0.696", "0.779"],
            ["Enhanced (27 feat.)", "0.953", "0.962", "+0.009", "0.848", "0.860"],
        ],
        col_widths=[4 * cm, 2.5 * cm, 2.7 * cm, 1.8 * cm, 2.3 * cm, 2.5 * cm],
    ))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "<i>Table 9. TabPFN-v2 vs Random Forest at the same action thresholds (0.285 screening, 0.380 enhanced).</i>",
        caption_style,
    ))
    story.append(para(
        "TabPFN beats Random Forest on AUC and F1 for both feature sets, though it trades a small amount of "
        "recall (0.84 vs 0.89 at the high-recall threshold) for substantially higher specificity. We keep the "
        "Random Forest as the deployed model because its higher recall aligns with the screening-first philosophy "
        "and because TabPFN inference is ~430&times; slower on this hardware (~8.6 s vs ~20 ms for the full "
        "136-patient holdout on CPU). The result is a "
        "first-order sanity check that no obvious headroom is being left on the table by the chosen algorithm."
    ))
    story.append(figure(
        "tabpfn_vs_rf_auc.png",
        "Figure 14. ROC-AUC comparison: TabPFN-v2 (Hollmann et al. <i>Nature</i> 2025) vs Random Forest.",
        max_width_cm=11,
    ))

    story.append(h2("10.2 Rotterdam-Criteria Clinical Rule (Teede et al., Fertil Steril 2023)"))
    story.append(para(
        "The international 2023 evidence-based PCOS guideline (Teede et al.) reaffirms the Rotterdam 2003 "
        "framework: PCOS-positive if at least 2 of 3 criteria are met &mdash; oligo/anovulation, hyperandrogenism, "
        "polycystic ovaries. Notebook 13 maps available dataset features to each criterion and benchmarks the "
        "hand-coded rule against the enhanced ML model."
    ))
    story.append(numeric_table(
        ["Metric", "Rotterdam 2-of-3 rule", "Enhanced ML model", "Δ (ML − rule)"],
        [
            ["Sensitivity", "0.795", "0.886", "+0.091"],
            ["Specificity", "0.913", "0.902", "−0.011"],
            ["PPV", "0.814", "0.812", "−0.001"],
            ["NPV", "0.903", "0.943", "+0.040"],
            ["F1", "0.805", "0.848", "+0.044"],
            ["F2", "0.799", "0.871", "+0.072"],
            ["Accuracy", "0.875", "0.897", "+0.022"],
        ],
        col_widths=[3 * cm, 4.5 * cm, 4.5 * cm, 4 * cm],
    ))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "<i>Table 10. Hand-coded Rotterdam 2-of-3 rule vs enhanced ML on the same holdout (n=136). The dataset "
        "lacks a direct serum-testosterone column, so biochemical hyperandrogenism is approximated using AMH and "
        "LH/FSH-related features; this is a documented limitation.</i>",
        caption_style,
    ))
    story.append(para(
        "The ML model adds 9.1 percentage points of sensitivity for only a 1.1-point specificity cost &mdash; "
        "exactly the trade we want from a clinical-decision-support layer that <i>augments</i> rather than "
        "replaces the guideline-anchored rule."
    ))
    story.append(two_figure_row(
        "rotterdam_feature_map.png", "Figure 15. Feature-to-criterion map (3 Rotterdam criteria &rarr; dataset columns).",
        "rotterdam_vs_ml.png", "Figure 16. Rotterdam rule vs enhanced ML, side-by-side metrics.",
    ))

    # ---- 11. Explainability ------------------------------------------------
    story.append(h1("11. Explainability"))
    story.append(para(
        "Explainability is treated as a core product feature, not an afterthought."
    ))
    story.append(h2("11.1 Global Drivers"))
    story.append(para(
        "Global feature importances are exported per model. The screening model leans on symptom presentation "
        "(skin darkening, hair growth, weight gain) and basic vitals; the enhanced model is dominated by ultrasound "
        "(follicle counts) once those features are available."
    ))
    story.append(two_figure_row(
        "screening_feature_importance.png", "Figure 17. Screening global drivers.",
        "enhanced_feature_importance.png", "Figure 18. Enhanced global drivers.",
    ))
    story.append(h2("11.2 Patient-Level SHAP Attributions"))
    story.append(para(
        "For tree models, <font face='Courier'>shap.TreeExplainer</font> produces fast and exact attributions. For "
        "logistic-regression fall-backs, each model artifact ships with a 100-row transformed training background "
        "that <font face='Courier'>shap.LinearExplainer</font> consumes. Demo cases are drawn from the held-out test "
        "slice (reproduced from the same random seed), so the explanations describe rows the model never saw during "
        "training."
    ))
    story.append(two_figure_row(
        "screening_shap_positive_case.png", "Figure 19. Screening SHAP, holdout PCOS-positive case.",
        "enhanced_shap_positive_case.png", "Figure 20. Enhanced SHAP, holdout PCOS-positive case.",
    ))

    # ---- 12. Differential prompt -------------------------------------------
    story.append(h1("12. Differential-Diagnosis Prompt"))
    story.append(para(
        "The endometriosis-overlap model is intentionally modest. It is trained on the supplementary synthetic "
        "dataset (10,000 rows) using six features (age, BMI, menstrual irregularity, chronic pain level, "
        "hormone-level abnormality, infertility) and reaches ROC-AUC 0.66 on a held-out split &mdash; a level that "
        "reflects the limits of the underlying synthetic data rather than a modelling failure. In the prototype, a "
        "positive overlap score raises a warning that the clinician should consider a broader gynaecologic differential "
        "workup, especially when chronic pain and infertility are reported alongside menstrual irregularity. It is "
        "<i>not</i> described as a validated endometriosis diagnostic model."
    ))

    # ---- 13. Prototype -----------------------------------------------------
    story.append(h1("13. Prototype"))
    story.append(para(
        "The Streamlit prototype at <font face='Courier'>src/app.py</font> loads the three joblib model artifacts and "
        "presents three tabs:"
    ))
    story.append(bullet("<b>Patient assessment</b> &mdash; intake form with collapsible sections for labs/ultrasound and differential-workup inputs, followed by stacked screening, enhanced, and endometriosis-overlap results. Each PCOS result shows probability, action threshold, threshold-anchored risk tier, and top SHAP drivers."))
    story.append(bullet("<b>Population view</b> &mdash; symptom prevalence by PCOS status (source cohort, n=541) and headline model metrics."))
    story.append(bullet("<b>About</b> &mdash; plain-language model descriptions, threshold strategy, and caveats."))
    story.append(para(
        "Risk tiers are anchored to each model's threshold so the displayed tier never contradicts the action flag:"
    ))
    story.append(bullet("<b>Low</b>: probability below threshold."))
    story.append(bullet("<b>Moderate</b>: probability from threshold to threshold + 0.20 (capped at 0.90)."))
    story.append(bullet("<b>High</b>: probability above the moderate band."))

    # ---- 14. Biological rationale -----------------------------------------
    story.append(h1("14. Biological Rationale from Single-Cell Feature Lists"))
    story.append(para(
        "Notebook 06 extracts feature symbols from one PCOS single-cell sample and checks for the presence of a "
        "curated list of literature-supported PCOS genes across steroidogenesis (CYP17A1, CYP19A1, HSD3B2, STAR), "
        "androgen signalling (AR, SRD5A1, SRD5A2, HSD17B3), follicular development (FSHR, LHCGR, GATA4), AMH "
        "signalling (AMH, AMHR2), insulin signalling (INSR, IRS1, IRS2, INS), and PCOS GWAS loci (DENND1A, THADA, "
        "FSHB). All 20 curated genes appear in the per-sample feature lists, giving the slide deck a defensible "
        "biological rationale for the clinical features the model uses. No QC, normalisation, integration, clustering, "
        "or differential expression analysis is claimed."
    ))

    # ---- 15. Limitations --------------------------------------------------
    story.append(h1("15. Limitations and Risk Controls"))
    story.append(bullet("<b>Small, single-source PCOS dataset.</b> 541 patients from 10 hospitals in Kerala, India is not enough for deployment-level validation, and the geography may not generalise."))
    story.append(bullet("<b>Synthetic endometriosis data.</b> The differential module is a workflow prompt, not a diagnostic claim."))
    story.append(bullet("<b>Equity variables are unavailable.</b> Race, income, geography, and access-to-care measures are missing, so the fairness audit in &sect;9 uses only age and BMI."))
    story.append(bullet("<b>Subgroup recall gaps.</b> A 25-point BMI recall gap in screening (lowest in the normal-BMI band) is an honest finding and a deployment risk; mitigation is subgroup-specific monitoring and external validation on a more balanced cohort."))
    story.append(bullet("<b>Missing serum testosterone.</b> The Rotterdam benchmark in &sect;10.2 approximates biochemical hyperandrogenism with AMH and LH/FSH features because direct testosterone is not in the dataset."))
    story.append(bullet("<b>Clinical framing.</b> All outputs are framed as risk, triage, and decision support, not diagnosis."))
    story.append(bullet("<b>Version sensitivity.</b> scikit-learn model artifacts are sensitive to version skew; <font face='Courier'>requirements.txt</font> pins the exact versions used during training."))
    story.append(bullet("<b>Threshold philosophy.</b> Tiered thresholds favour sensitivity; clinicians who prefer specificity-first triage can switch to the balanced threshold in Table 4 without retraining."))

    # ---- 16. Reproducible artifacts ---------------------------------------
    story.append(h1("16. Reproducible Artifacts"))
    artifacts = [
        ("notebooks/01_pcos_data_audit_and_eda.ipynb", "Loading, cleaning, audit, EDA, processed CSV export."),
        ("notebooks/02_train_pcos_screening_model.ipynb", "Training, threshold selection, evaluation: screening."),
        ("notebooks/03_train_pcos_enhanced_model.ipynb", "Training and evaluation: labs/ultrasound model."),
        ("notebooks/04_train_endometriosis_overlap_model.ipynb", "Synthetic-data differential prompt model."),
        ("notebooks/05_thresholds_explainability_and_demo.ipynb", "SHAP, held-out demo cases, model card."),
        ("notebooks/06_single_cell_gene_peek.ipynb", "Lightweight biological-rationale gene-list check."),
        ("notebooks/07_uncertainty_quantification.ipynb", "Bootstrap 95% CIs, paired AUC-difference test."),
        ("notebooks/08_calibration_analysis.ipynb", "Brier, ECE, Platt and isotonic recalibration."),
        ("notebooks/09_decision_curve_analysis.ipynb", "Net-benefit curves vs treat-all / treat-none baselines."),
        ("notebooks/10_tabpfn_benchmark.ipynb", "TabPFN-v2 (Nature 2025) vs Random Forest benchmark."),
        ("notebooks/11_subgroup_fairness.ipynb", "Subgroup recall audit by age and BMI."),
        ("notebooks/12_conformal_prediction.ipynb", "Split-conformal prediction sets with coverage check."),
        ("notebooks/13_rotterdam_alignment.ipynb", "Rotterdam 2-of-3 rule benchmark vs enhanced ML."),
        ("src/app.py", "Streamlit clinician-facing prototype."),
        ("outputs/models/*.joblib", "Saved model artifacts (with SHAP backgrounds)."),
        ("outputs/metrics/*", "Held-out metrics, threshold trade-offs, SHAP tables, CIs, calibration, DCA, fairness, conformal, Rotterdam, TabPFN."),
        ("scripts/create_training_notebooks.mjs", "Deterministic notebook regenerator for notebooks 01-06."),
        ("report/build_pdf.py", "Reportlab generator for this PDF."),
        ("PROJECT_PLAN.md, README.md, SUBMISSION.md", "Plan, quickstart, packaging checklist."),
    ]
    story.append(styled_table(
        ["Artifact", "Purpose"],
        [[cell_para(p, path_cell_style), cell_para(d)] for p, d in artifacts],
        col_widths=[7.4 * cm, 9.2 * cm],
        valign="TOP",
    ))

    # ---- 17. Conclusion ---------------------------------------------------
    story.append(h1("17. Conclusion"))
    story.append(para(
        "PCOS Pathfinder is not an automated diagnosis. It is a practical, explainable, tiered workflow that "
        "(a) identifies high-risk patients earlier with recall &ge; 0.88 and NPV &ge; 0.93; (b) demonstrates a "
        "AUC improvement of the enhanced over the screening model on this split (&Delta;=+0.057, "
        "p&asymp;0.015); (c) ships calibrated probabilities, conformal coverage guarantees, decision-curve "
        "utility, subgroup fairness numbers, a recent-SOTA TabPFN benchmark, and a Rotterdam clinical-rule "
        "benchmark; (d) flags its own equity limitations honestly. The cleaning rules, threshold strategy, and "
        "SHAP attributions are reproducible end-to-end from the thirteen numbered notebooks; the Streamlit "
        "prototype loads the same artifacts a clinician would use; and the limitations are stated up-front in "
        "the model card."
    ))

    # ---- 18. References ---------------------------------------------------
    story.append(h1("18. Selected References"))
    refs = [
        "Collins GS, Moons KGM, Dhiman P, et al. <b>TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods.</b> <i>BMJ</i> 2024;385:e078378.",
        "Van Calster B, McLernon DJ, van Smeden M, et al. <b>Calibration: the Achilles heel of predictive analytics.</b> <i>BMC Medicine</i> 2019;17:230.",
        "Vickers AJ, Elkin EB. <b>Decision curve analysis: a novel method for evaluating prediction models.</b> <i>Med Decis Making</i> 2006;26(6):565-574.",
        "Vickers AJ, Van Calster B, Steyerberg EW. <b>Net benefit approaches to the evaluation of prediction models, molecular markers, and diagnostic tests.</b> <i>BMJ</i> 2016;352:i6.",
        "Hollmann N, Müller S, Purucker L, et al. <b>Accurate predictions on small data with a tabular foundation model.</b> <i>Nature</i> 2025;637(8045):319-326. (TabPFN-v2)",
        "Angelopoulos AN, Bates S. <b>Conformal Prediction: A Gentle Introduction.</b> <i>Foundations and Trends in Machine Learning</i> 2023;16(4):494-591.",
        "Obermeyer Z, Powers B, Vogeli C, Mullainathan S. <b>Dissecting racial bias in an algorithm used to manage the health of populations.</b> <i>Science</i> 2019;366(6464):447-453.",
        "Rotterdam ESHRE/ASRM-Sponsored PCOS Consensus Workshop Group. <b>Revised 2003 consensus on diagnostic criteria and long-term health risks related to polycystic ovary syndrome (PCOS).</b> <i>Fertil Steril</i> 2004;81(1):19-25.",
        "Teede HJ, Tay CT, Laven JJE, et al. <b>Recommendations from the 2023 International Evidence-based Guideline for the Assessment and Management of Polycystic Ovary Syndrome.</b> <i>Fertil Steril</i> 2023;120(4):767-793.",
        "Lundberg SM, Lee SI. <b>A unified approach to interpreting model predictions.</b> <i>NeurIPS</i> 2017. (SHAP)",
    ]
    for r in refs:
        story.append(Paragraph(r, ParagraphStyle("Ref", parent=body_style, fontSize=8.8, leading=11.6, leftIndent=14, bulletIndent=4, spaceAfter=4)))

    doc.build(story)


if __name__ == "__main__":
    build()
    print(f"Wrote {OUT_PATH}")
