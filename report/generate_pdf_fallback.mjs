import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.join(path.dirname(fileURLToPath(import.meta.url)), ".."));
const reportDir = path.join(root, "report");
const imageDir = path.join(reportDir, "build_images");
const outPath = path.join(reportDir, "pcos_pathfinder_report.pdf");

function pdfEscape(value) {
  return String(value)
    .replace(/\\/g, "\\\\")
    .replace(/\(/g, "\\(")
    .replace(/\)/g, "\\)")
    .replace(/[^\x09\x0A\x0D\x20-\x7E]/g, "");
}

function jpegInfo(buffer) {
  if (buffer[0] !== 0xff || buffer[1] !== 0xd8) throw new Error("Not a JPEG file");
  let offset = 2;
  while (offset < buffer.length) {
    if (buffer[offset] !== 0xff) {
      offset++;
      continue;
    }
    const marker = buffer[offset + 1];
    const length = buffer.readUInt16BE(offset + 2);
    if ([0xc0, 0xc1, 0xc2].includes(marker)) {
      return {
        height: buffer.readUInt16BE(offset + 5),
        width: buffer.readUInt16BE(offset + 7),
      };
    }
    offset += 2 + length;
  }
  throw new Error("JPEG dimensions not found");
}

class PdfBuilder {
  constructor() {
    this.objects = [null];
  }

  addObject(content) {
    this.objects.push(content);
    return this.objects.length - 1;
  }

  setObject(id, content) {
    this.objects[id] = content;
  }

  reserveObject() {
    this.objects.push(null);
    return this.objects.length - 1;
  }

  streamObject(dict, data) {
    const header = Buffer.from(`<< ${dict} /Length ${data.length} >>\nstream\n`, "binary");
    const footer = Buffer.from("\nendstream", "binary");
    return Buffer.concat([header, data, footer]);
  }

  write(catalogId, filePath) {
    const chunks = [Buffer.from("%PDF-1.4\n%\xE2\xE3\xCF\xD3\n", "binary")];
    const offsets = [0];
    for (let i = 1; i < this.objects.length; i++) {
      offsets[i] = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
      const content = Buffer.isBuffer(this.objects[i])
        ? this.objects[i]
        : Buffer.from(String(this.objects[i]), "binary");
      chunks.push(Buffer.from(`${i} 0 obj\n`, "binary"), content, Buffer.from("\nendobj\n", "binary"));
    }
    const xrefOffset = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
    let xref = `xref\n0 ${this.objects.length}\n0000000000 65535 f \n`;
    for (let i = 1; i < this.objects.length; i++) {
      xref += `${String(offsets[i]).padStart(10, "0")} 00000 n \n`;
    }
    xref += `trailer\n<< /Size ${this.objects.length} /Root ${catalogId} 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`;
    chunks.push(Buffer.from(xref, "binary"));
    fs.writeFileSync(filePath, Buffer.concat(chunks));
  }
}

const pdf = new PdfBuilder();
const pagesId = pdf.reserveObject();
const fontRegularId = pdf.addObject("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>");
const fontBoldId = pdf.addObject("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>");

const imageSpecs = [
  ["pcos_class_balance.jpg", "Class balance in the required PCOS dataset."],
  ["pcos_symptom_rates.jpg", "Source-cohort symptom prevalence by PCOS status."],
  ["screening_roc_curve.jpg", "Screening model ROC curve."],
  ["enhanced_roc_curve.jpg", "Enhanced model ROC curve."],
  ["screening_confusion_matrix.jpg", "Screening model confusion matrix."],
  ["enhanced_confusion_matrix.jpg", "Enhanced model confusion matrix."],
  ["screening_feature_importance.jpg", "Screening model global drivers."],
  ["enhanced_feature_importance.jpg", "Enhanced model global drivers."],
  ["screening_shap_positive_case.jpg", "Screening SHAP drivers for a held-out PCOS-positive case."],
  ["enhanced_shap_positive_case.jpg", "Enhanced SHAP drivers for a held-out PCOS-positive case."],
];

const images = {};
let imageCounter = 1;
for (const [fileName, caption] of imageSpecs) {
  const fullPath = path.join(imageDir, fileName);
  if (!fs.existsSync(fullPath)) continue;
  const data = fs.readFileSync(fullPath);
  const { width, height } = jpegInfo(data);
  const name = `Im${imageCounter++}`;
  const objectId = pdf.addObject(pdf.streamObject(
    `/Type /XObject /Subtype /Image /Width ${width} /Height ${height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode`,
    data,
  ));
  images[fileName] = { name, objectId, width, height, caption };
}

const PAGE_W = 612;
const PAGE_H = 792;
const MARGIN = 54;
const BOTTOM = 54;
const BODY_W = PAGE_W - 2 * MARGIN;
const pages = [];
let commands = [];
let y = PAGE_H - MARGIN;
let pageNumber = 0;

function lineHeight(size) {
  return size * 1.35;
}

function newPage() {
  if (commands.length) finishPage();
  commands = [];
  y = PAGE_H - MARGIN;
  pageNumber++;
}

function finishPage() {
  if (pageNumber > 0) {
    text(`PCOS Pathfinder Technical Report | ${pageNumber}`, MARGIN, 28, 8, "F1");
  }
  const content = Buffer.from(commands.join("\n"), "binary");
  const contentId = pdf.addObject(pdf.streamObject("", content));
  const xobjects = Object.values(images).map((im) => `/${im.name} ${im.objectId} 0 R`).join(" ");
  const resources = `<< /Font << /F1 ${fontRegularId} 0 R /F2 ${fontBoldId} 0 R >> /XObject << ${xobjects} >> >>`;
  const pageId = pdf.addObject(`<< /Type /Page /Parent ${pagesId} 0 R /MediaBox [0 0 ${PAGE_W} ${PAGE_H}] /Resources ${resources} /Contents ${contentId} 0 R >>`);
  pages.push(pageId);
}

function ensureSpace(height) {
  if (y - height < BOTTOM) newPage();
}

function text(value, x, yy, size = 10, font = "F1") {
  commands.push(`BT /${font} ${size} Tf 1 0 0 1 ${x.toFixed(2)} ${yy.toFixed(2)} Tm (${pdfEscape(value)}) Tj ET`);
}

function wrap(value, maxWidth, size) {
  const words = String(value).split(/\s+/).filter(Boolean);
  const lines = [];
  let current = "";
  const maxChars = Math.max(20, Math.floor(maxWidth / (size * 0.50)));
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length > maxChars && current) {
      lines.push(current);
      current = word;
    } else {
      current = next;
    }
  }
  if (current) lines.push(current);
  return lines;
}

function paragraph(value, size = 10, gap = 8) {
  const wrapped = wrap(value, BODY_W, size);
  ensureSpace(wrapped.length * lineHeight(size) + gap);
  for (const line of wrapped) {
    text(line, MARGIN, y, size, "F1");
    y -= lineHeight(size);
  }
  y -= gap;
}

function heading(value, level = 1) {
  const size = level === 1 ? 17 : 13;
  const gapTop = level === 1 ? 16 : 10;
  ensureSpace(gapTop + lineHeight(size) + 8);
  y -= gapTop;
  text(value, MARGIN, y, size, "F2");
  y -= lineHeight(size) + 4;
}

function bullets(items) {
  for (const item of items) {
    const wrapped = wrap(item, BODY_W - 18, 10);
    ensureSpace(wrapped.length * lineHeight(10) + 3);
    text("-", MARGIN, y, 10, "F2");
    text(wrapped[0], MARGIN + 18, y, 10, "F1");
    y -= lineHeight(10);
    for (let i = 1; i < wrapped.length; i++) {
      text(wrapped[i], MARGIN + 18, y, 10, "F1");
      y -= lineHeight(10);
    }
    y -= 2;
  }
  y -= 4;
}

function table(headers, rows, widths) {
  const rowH = 16;
  ensureSpace((rows.length + 2) * rowH + 10);
  let x = MARGIN;
  for (let i = 0; i < headers.length; i++) {
    text(headers[i], x, y, 9, "F2");
    x += widths[i];
  }
  y -= rowH;
  for (const row of rows) {
    x = MARGIN;
    for (let i = 0; i < row.length; i++) {
      text(row[i], x, y, 9, "F1");
      x += widths[i];
    }
    y -= rowH;
  }
  y -= 8;
}

function image(fileName, width = BODY_W) {
  const im = images[fileName];
  if (!im) return;
  const height = width * im.height / im.width;
  ensureSpace(height + 34);
  const x = MARGIN + (BODY_W - width) / 2;
  y -= height;
  commands.push(`q ${width.toFixed(2)} 0 0 ${height.toFixed(2)} ${x.toFixed(2)} ${y.toFixed(2)} cm /${im.name} Do Q`);
  y -= 14;
  const cap = wrap(im.caption, BODY_W, 8.5);
  for (const line of cap) {
    text(line, MARGIN, y, 8.5, "F1");
    y -= lineHeight(8.5);
  }
  y -= 8;
}

newPage();

text("PCOS Pathfinder", MARGIN, y, 28, "F2");
y -= 34;
text("Technical Report for Biohackathon 2026: Women's Health", MARGIN, y, 14, "F1");
y -= 24;
text("11-22 May 2026", MARGIN, y, 11, "F1");
y -= 38;

paragraph("PCOS Pathfinder is a tiered clinical decision-support prototype for earlier identification of Polycystic Ovary Syndrome (PCOS) and broader differential workup in women's health. It combines a required-dataset modelling core, explainability, an endometriosis-overlap prompt, and a Streamlit prototype.");
image("pcos_class_balance.jpg", 330);

heading("1. Challenge Context");
paragraph("The hackathon challenge asks teams to improve diagnostic accuracy for women's health conditions using available data and a feasible implementation pathway. PCOS is the core case because it is common, heterogeneous, and frequently diagnosed late.");
bullets([
  "Frontline screening model: high-recall triage using symptoms and basic vitals.",
  "Enhanced diagnostic-support model: adds labs and ultrasound markers.",
  "Endometriosis-overlap prompt: a workflow nudge for broader differential workup, not a diagnosis.",
]);

heading("2. Data Sources");
table(["Dataset", "Rows", "Use"], [
  ["PCOS clinical", "541", "Required modelling foundation"],
  ["Endometriosis synthetic", "10,000", "Differential-overlap prompt"],
  ["PCOS single-cell", "20 samples", "Biological rationale peek"],
  ["Endometrium single-cell", "2 samples", "Biological context only"],
], [150, 90, 270]);
paragraph("The PCOS dataset comes from 10 hospitals across Kerala, India. The target split is 364 non-PCOS and 177 PCOS cases. The supplementary endometriosis dataset is synthetic, so it is used only as a workflow prompt.");

heading("3. Data Cleaning and Quality Controls");
bullets([
  "Dropped identifiers: sl_no and patient_file_no.",
  "Dropped blood_group because codes 11-18 have no meaningful ordinal interpretation.",
  "Dropped marriage_status_yrs because it is clinically sensitive and not a defensible diagnostic signal.",
  "Excluded fast_food_y_n and reg_exercise_y_n from the screening model to reduce stigma and bias.",
  "Logged two coerced non-numeric values: 1.99. in II beta-HCG and a in AMH.",
  "Relabelled Cycle length(days) as duration of menses bleeding, because the observed range is 0-12 with median 5.",
]);
image("pcos_symptom_rates.jpg", BODY_W);

heading("4. Model Design");
paragraph("The screening model uses age, BMI, cycle regularity, engineered cycle-irregular flag, duration of menses bleeding, weight gain, hair growth, skin darkening, hair loss, pimples, random blood sugar, and blood pressure. The enhanced model adds hemoglobin, FSH, LH, FSH/LH, TSH, AMH, prolactin, vitamin D3, progesterone, follicle counts, follicle sizes, and endometrium thickness.");
paragraph("Both PCOS notebooks compare a dummy baseline, logistic regression, random forest, and gradient boosting. Thresholds are selected on training out-of-fold probabilities, then evaluated once on the held-out test set.");

heading("5. Held-Out Results");
table(["Model", "Threshold", "ROC-AUC", "Recall", "Specificity", "F1"], [
  ["Screening", "0.285", "0.896", "0.886", "0.685", "0.696"],
  ["Enhanced", "0.380", "0.953", "0.886", "0.902", "0.848"],
  ["Endometriosis overlap", "0.510", "0.660", "0.628", "0.618", "0.576"],
], [145, 78, 78, 70, 86, 55]);
paragraph("The enhanced model improves specificity and F1 while preserving the same held-out recall as the screening model. The screening model remains useful for low-resource triage, while the enhanced model is better suited for specialist or post-investigation support.");
image("screening_roc_curve.jpg", 245);
image("enhanced_roc_curve.jpg", 245);
image("screening_confusion_matrix.jpg", 245);
image("enhanced_confusion_matrix.jpg", 245);

heading("6. Explainability");
paragraph("Explainability is a core feature. Global feature importance is exported for the model card and slide deck. Patient-level SHAP attributions are produced for held-out demo cases and surfaced in the Streamlit app.");
bullets([
  "Screening top drivers: skin darkening, hair growth, weight gain, BMI, menses duration, age, and random blood sugar.",
  "Enhanced top drivers: right and left follicle counts, skin darkening, weight gain, hair growth, AMH, menses duration, BMI, and cycle regularity.",
]);
image("screening_feature_importance.jpg", BODY_W);
image("enhanced_feature_importance.jpg", BODY_W);
image("screening_shap_positive_case.jpg", BODY_W);
image("enhanced_shap_positive_case.jpg", BODY_W);

heading("7. Prototype");
paragraph("The Streamlit app at src/app.py loads the three joblib artifacts and presents Patient assessment, Population view, and About tabs. It displays probability, action threshold, risk tier, SHAP drivers, and an endometriosis-overlap warning when relevant.");
bullets([
  "Risk tiers are anchored to each model threshold so display labels do not contradict action flags.",
  "Population view is labelled as source cohort because symptom rates are computed on the full 541-row dataset before any train/test split.",
  "The app stores a transformed SHAP background in each model artifact for future logistic-regression explanations.",
]);

heading("8. Limitations");
bullets([
  "The PCOS dataset is small and single-source; external validation is required before clinical deployment.",
  "The endometriosis dataset is synthetic; its model is a workflow prompt only.",
  "Equity claims are limited because race, income, access-to-care, and geography variables are unavailable.",
  "All outputs must be framed as decision support, not standalone diagnosis.",
  "Scikit-learn artifacts are version-sensitive, so dependencies are pinned in requirements.txt.",
]);

heading("9. Reproducible Artifacts");
bullets([
  "Six numbered notebooks cover EDA, PCOS screening, enhanced diagnosis, endometriosis overlap, SHAP/demo cases, and single-cell gene peek.",
  "outputs/models contains the three joblib artifacts.",
  "outputs/metrics contains hold-out metrics, CV tables, SHAP tables, model card, and audit reports.",
  "PROJECT_PLAN.md and SUBMISSION.md document the design and packaging checklist.",
  "report/pcos_pathfinder_report.tex is the LaTeX source for this report.",
]);

heading("10. Conclusion");
paragraph("The strongest claim for PCOS Pathfinder is not automated diagnosis. It is a practical, explainable workflow that helps clinicians identify high-risk patients earlier, choose appropriate next investigations, and avoid overlooking overlapping women's health conditions.");

finishPage();
const catalogId = pdf.addObject(`<< /Type /Catalog /Pages ${pagesId} 0 R >>`);
pdf.setObject(pagesId, `<< /Type /Pages /Kids [${pages.map((id) => `${id} 0 R`).join(" ")}] /Count ${pages.length} >>`);
pdf.write(catalogId, outPath);

console.log(outPath);
