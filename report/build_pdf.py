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
        "rationale. The delivered artifacts are six reproducible notebooks, three saved scikit-learn models, a "
        "Streamlit clinician interface, exported metrics and figures, and this report. Thresholds are selected "
        "from out-of-fold training probabilities (no test leakage), risk tiers are anchored to each model's "
        "action threshold, and patient-level SHAP attributions are provided for both PCOS models. On the held-out "
        "test split the enhanced model reaches ROC-AUC 0.953 with recall 0.886 and specificity 0.902. The system "
        "is framed throughout as decision support, not standalone diagnosis.",
        abstract_body,
    ))

    story.append(Spacer(1, 0.3 * cm))
    headline = [
        ["Headline metric", "Screening", "Enhanced"],
        ["ROC-AUC", "0.896", "0.953"],
        ["Recall (sensitivity)", "0.886", "0.886"],
        ["Specificity", "0.685", "0.902"],
        ["NPV (rule-out value)", "0.926", "0.943"],
        ["F2 score", "0.799", "0.871"],
    ]
    story.append(numeric_table(headline[0], headline[1:], col_widths=[6 * cm, 4.5 * cm, 4.5 * cm]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "<i>Held-out test split (n=136) at CV-selected high-recall thresholds. "
        "F1 is deliberately suppressed by the high-recall threshold &mdash; see &sect;6.2.</i>",
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
    story.append(h2("6.1 Held-Out Performance at the Chosen Thresholds"))
    story.append(numeric_table(
        ["Model", "Thresh.", "ROC-AUC", "Recall", "Spec.", "PPV", "NPV", "F2"],
        [
            ["Screening", "0.285", "0.896", "0.886", "0.685", "0.574", "0.926", "0.799"],
            ["Enhanced", "0.380", "0.953", "0.886", "0.902", "0.812", "0.943", "0.871"],
            ["Endo (synth.)", "0.510", "0.660", "0.628", "0.618", "0.531", "—", "0.609"],
        ],
        col_widths=[3.0 * cm, 1.7 * cm, 2.0 * cm, 1.7 * cm, 1.6 * cm, 1.6 * cm, 1.6 * cm, 1.6 * cm],
    ))
    story.append(Spacer(1, 0.2 * cm))
    story.append(para(
        "The enhanced model improves specificity (0.685 &rarr; 0.902) and precision (0.574 &rarr; 0.812) while "
        "preserving the same recall as the screening model. NPV is 0.926 for screening and 0.943 for enhanced &mdash; "
        "when either model says \"no PCOS\", it is right &gt;92% of the time, which is the right framing for "
        "ruling-out triage."
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
        "screening_roc_curve.png", "Figure 2. Screening ROC, AUC = 0.896.",
        "enhanced_roc_curve.png", "Figure 3. Enhanced ROC, AUC = 0.953.",
    ))
    story.append(two_figure_row(
        "screening_confusion_matrix.png", "Figure 4. Screening confusion at t = 0.285.",
        "enhanced_confusion_matrix.png", "Figure 5. Enhanced confusion at t = 0.380.",
    ))

    # ---- 7. Explainability ------------------------------------------------
    story.append(h1("7. Explainability"))
    story.append(para(
        "Explainability is treated as a core product feature, not an afterthought."
    ))
    story.append(h2("7.1 Global Drivers"))
    story.append(para(
        "Global feature importances are exported per model. The screening model leans on symptom presentation "
        "(skin darkening, hair growth, weight gain) and basic vitals; the enhanced model is dominated by ultrasound "
        "(follicle counts) once those features are available."
    ))
    story.append(two_figure_row(
        "screening_feature_importance.png", "Figure 6. Screening global drivers.",
        "enhanced_feature_importance.png", "Figure 7. Enhanced global drivers.",
    ))

    story.append(h2("7.2 Patient-Level SHAP Attributions"))
    story.append(para(
        "For tree models, <font face='Courier'>shap.TreeExplainer</font> produces fast and exact attributions. For "
        "logistic-regression fall-backs, each model artifact ships with a 100-row transformed training background "
        "that <font face='Courier'>shap.LinearExplainer</font> consumes. Demo cases are drawn from the held-out test "
        "slice (reproduced from the same random seed), so the explanations describe rows the model never saw during "
        "training."
    ))
    story.append(two_figure_row(
        "screening_shap_positive_case.png", "Figure 8. Screening SHAP, holdout PCOS-positive case.",
        "enhanced_shap_positive_case.png", "Figure 9. Enhanced SHAP, holdout PCOS-positive case.",
    ))

    # ---- 8. Differential prompt -------------------------------------------
    story.append(h1("8. Differential-Diagnosis Prompt"))
    story.append(para(
        "The endometriosis-overlap model is intentionally modest. It is trained on the supplementary synthetic "
        "dataset (10,000 rows) using six features (age, BMI, menstrual irregularity, chronic pain level, "
        "hormone-level abnormality, infertility) and reaches ROC-AUC 0.66 on a held-out split &mdash; a level that "
        "reflects the limits of the underlying synthetic data rather than a modelling failure. In the prototype, a "
        "positive overlap score raises a warning that the clinician should consider a broader gynaecologic differential "
        "workup, especially when chronic pain and infertility are reported alongside menstrual irregularity. It is "
        "<i>not</i> described as a validated endometriosis diagnostic model."
    ))

    # ---- 9. Prototype -----------------------------------------------------
    story.append(h1("9. Prototype"))
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

    # ---- 10. Biological rationale -----------------------------------------
    story.append(h1("10. Biological Rationale from Single-Cell Feature Lists"))
    story.append(para(
        "Notebook 06 extracts feature symbols from one PCOS single-cell sample and checks for the presence of a "
        "curated list of literature-supported PCOS genes across steroidogenesis (CYP17A1, CYP19A1, HSD3B2, STAR), "
        "androgen signalling (AR, SRD5A1, SRD5A2, HSD17B3), follicular development (FSHR, LHCGR, GATA4), AMH "
        "signalling (AMH, AMHR2), insulin signalling (INSR, IRS1, IRS2, INS), and PCOS GWAS loci (DENND1A, THADA, "
        "FSHB). All 20 curated genes appear in the per-sample feature lists, giving the slide deck a defensible "
        "biological rationale for the clinical features the model uses. No QC, normalisation, integration, clustering, "
        "or differential expression analysis is claimed."
    ))

    # ---- 11. Limitations --------------------------------------------------
    story.append(h1("11. Limitations and Risk Controls"))
    story.append(bullet("<b>Small, single-source PCOS dataset.</b> 541 patients from 10 hospitals in Kerala, India is not enough for deployment-level validation, and the geography may not generalise."))
    story.append(bullet("<b>Synthetic endometriosis data.</b> The differential module is a workflow prompt, not a diagnostic claim."))
    story.append(bullet("<b>Equity variables are unavailable.</b> Race, income, geography, and access-to-care measures are missing, so equity claims rest on workflow design and low-resource feasibility rather than measured outcome disparities."))
    story.append(bullet("<b>Clinical framing.</b> All outputs are framed as risk, triage, and decision support, not diagnosis."))
    story.append(bullet("<b>Version sensitivity.</b> scikit-learn model artifacts are sensitive to version skew; <font face='Courier'>requirements.txt</font> pins the exact versions used during training."))
    story.append(bullet("<b>Threshold philosophy.</b> Tiered thresholds favour sensitivity; clinicians who prefer specificity-first triage can switch to the balanced threshold reported in Table 4 without retraining."))

    # ---- 12. Reproducible artifacts ---------------------------------------
    story.append(h1("12. Reproducible Artifacts"))
    artifacts = [
        ("notebooks/01_pcos_data_audit_and_eda.ipynb", "Loading, cleaning, audit, EDA, processed CSV export."),
        ("notebooks/02_train_pcos_screening_model.ipynb", "Training, threshold selection, evaluation: screening."),
        ("notebooks/03_train_pcos_enhanced_model.ipynb", "Training and evaluation: labs/ultrasound model."),
        ("notebooks/04_train_endometriosis_overlap_model.ipynb", "Synthetic-data differential prompt model."),
        ("notebooks/05_thresholds_explainability_and_demo.ipynb", "SHAP, held-out demo cases, model card."),
        ("notebooks/06_single_cell_gene_peek.ipynb", "Lightweight biological-rationale gene-list check."),
        ("src/app.py", "Streamlit clinician-facing prototype."),
        ("outputs/models/*.joblib", "Saved model artifacts (with SHAP backgrounds)."),
        ("outputs/metrics/*", "Held-out metrics, threshold trade-offs, SHAP tables, model card."),
        ("scripts/create_training_notebooks.mjs", "Deterministic notebook regenerator (source of truth)."),
        ("report/build_pdf.py", "Reportlab generator for this PDF."),
        ("PROJECT_PLAN.md, README.md, SUBMISSION.md", "Plan, quickstart, packaging checklist."),
    ]
    story.append(styled_table(
        ["Artifact", "Purpose"],
        [[cell_para(p, path_cell_style), cell_para(d)] for p, d in artifacts],
        col_widths=[7.4 * cm, 9.2 * cm],
        valign="TOP",
    ))

    # ---- 13. Conclusion ---------------------------------------------------
    story.append(h1("13. Conclusion"))
    story.append(para(
        "The defensible pitch for PCOS Pathfinder is not automated diagnosis. It is a practical, explainable, "
        "tiered workflow that helps clinicians identify high-risk patients earlier (recall &ge; 0.88), choose "
        "appropriate next investigations (the enhanced model dominates F2 at the same recall), and avoid overlooking "
        "adjacent women's health conditions (the differential prompt). The cleaning rules, threshold strategy, and "
        "SHAP attributions are reproducible end-to-end from the six numbered notebooks; the Streamlit prototype loads "
        "the same artifacts a clinician would use; and the limitations are stated up-front in the model card."
    ))

    doc.build(story)


if __name__ == "__main__":
    build()
    print(f"Wrote {OUT_PATH}")
