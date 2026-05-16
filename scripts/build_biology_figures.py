"""Generate biology schematic figures for the PCOS Pathfinder pptx deck.

Figure dimensions match the slide embed box (8.20 x 4.85 inches in the
biology slide layout) at aspect ratio 1.69. That way matplotlib font sizes
in points equal apparent point sizes on the rendered slide — no scaling-
induced shrinkage.

Output: outputs/figures/biology/{hpo_axis, insulin_androgen, ovary_morphology,
phenotype_venn, single_cell_genes}.png at 1800x1062 px each.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import pandas as pd

OUT = Path("outputs/figures/biology")
OUT.mkdir(parents=True, exist_ok=True)

# On-brand palette (mirrors the HTML deck CSS variables).
NAVY = "#1f3a5f"
INK = "#14213d"
MUTED = "#5f6c7b"
TEAL = "#007c89"
CORAL = "#d95d39"
GOLD = "#c98910"
GREEN = "#2f855a"
LAV = "#6b5b95"
PAPER = "#fbfcfd"
SOFT_TEAL = "#e7f4f5"
SOFT_CORAL = "#fff0eb"
SOFT_GOLD = "#fff8e6"
SOFT_LAV = "#efeaf6"

# Figure dimensions match the biology slide's image embed box (8.20 x 4.85).
# Using 10.0 x 5.92 keeps the aspect ratio (1.69) and renders at 1800x1066 px
# at DPI 180 — comfortably under the 2000px API limit.
FIGSIZE = (10.0, 5.92)
DPI = 180

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "savefig.facecolor": PAPER,
        "figure.facecolor": PAPER,
    }
)


def _save(fig: plt.Figure, name: str) -> Path:
    path = OUT / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=PAPER,
                pad_inches=0.18)
    plt.close(fig)
    return path


def _node(ax, cx, cy, w, h, label, sub, color, bg, label_size=12, sub_size=10):
    box = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.10,rounding_size=0.15",
        linewidth=1.5, edgecolor=color, facecolor=bg,
    )
    ax.add_patch(box)
    ax.text(cx, cy + h * 0.18, label, ha="center", va="center",
            fontsize=label_size, fontweight="bold", color=color)
    ax.text(cx, cy - h * 0.22, sub, ha="center", va="center",
            fontsize=sub_size, color=MUTED)


def hpo_axis() -> Path:
    """Bio-1: HPO axis schematic — vertical chain + bullet panel."""
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title(
        "HPO axis: where PCOS hyperandrogenism arises",
        fontsize=17, fontweight="bold", color=NAVY, loc="left", pad=8,
    )

    # Three-stage column on the left, narrower so it fits at 10" wide.
    _node(ax, 1.55, 4.85, 2.5, 0.95, "Hypothalamus", "GnRH pulses",
          TEAL, SOFT_TEAL, label_size=13, sub_size=10.5)
    _node(ax, 1.55, 3.05, 2.5, 0.95, "Pituitary", "LH / FSH",
          LAV, SOFT_LAV, label_size=13, sub_size=10.5)
    _node(ax, 1.55, 1.25, 2.5, 0.95, "Ovary", "Theca + granulosa",
          CORAL, SOFT_CORAL, label_size=13, sub_size=10.5)

    def arrow(x1, y1, x2, y2, label, color):
        a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                            mutation_scale=18, linewidth=2.0, color=color)
        ax.add_patch(a)
        ax.text(x1 + 0.15, (y1 + y2) / 2, label, ha="left", va="center",
                fontsize=10.5, color=color, fontweight="bold")

    arrow(1.55, 4.35, 1.55, 3.55, "GnRH pulse", TEAL)
    arrow(1.55, 2.55, 1.55, 1.75, "↑ LH", LAV)

    # Right-side "In PCOS" panel.
    panel = FancyBboxPatch((3.40, 0.45), 6.45, 5.20,
                           boxstyle="round,pad=0.10,rounding_size=0.14",
                           linewidth=1.4, edgecolor=NAVY, facecolor="#f1f5f9")
    ax.add_patch(panel)
    ax.text(3.60, 5.30, "In PCOS", fontsize=15, fontweight="bold",
            color=NAVY, ha="left", va="top")

    bullets = [
        "Faster GnRH pulse frequency at the hypothalamus",
        "↑ LH relative to FSH (often LH:FSH ≥ 2)",
        "↑ Theca-cell androgen output",
        "↓ Aromatization of androgens to estradiol",
        "Follicular arrest at ~2–8 mm; no dominant follicle",
        "Clinical: hirsutism, acne, oligo-ovulation",
    ]
    for i, b in enumerate(bullets):
        y = 4.65 - i * 0.65
        ax.text(3.68, y, "•", fontsize=13, color=NAVY,
                fontweight="bold", ha="left", va="center")
        ax.text(3.92, y, b, fontsize=12, color=INK, ha="left", va="center")

    ax.text(0.05, 0.05,
            "Schematic only. ESHRE/Rotterdam consensus on PCOS pathophysiology.",
            fontsize=9, color=MUTED, ha="left", va="bottom")

    return _save(fig, "hpo_axis.png")


def insulin_androgen_loop() -> Path:
    """Bio-2: 4-box insulin/androgen feedback loop + long-term risk band."""
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Insulin resistance amplifies ovarian androgen output",
                 fontsize=17, fontweight="bold", color=NAVY, loc="left", pad=8)

    # Four nodes in a 2x2 grid.
    _node(ax, 2.30, 4.30, 3.40, 1.15, "Hyperinsulinemia",
          "from peripheral IR", TEAL, SOFT_TEAL,
          label_size=13, sub_size=10.5)
    _node(ax, 7.70, 4.30, 3.40, 1.15, "Ovarian theca",
          "↑ androgen synthesis", CORAL, SOFT_CORAL,
          label_size=13, sub_size=10.5)
    _node(ax, 2.30, 1.95, 3.40, 1.15, "Adipose / muscle",
          "insulin resistance", LAV, SOFT_LAV,
          label_size=13, sub_size=10.5)
    _node(ax, 7.70, 1.95, 3.40, 1.15, "Liver",
          "↓ SHBG → ↑ free T", GOLD, SOFT_GOLD,
          label_size=13, sub_size=10.5)

    def arrow(x1, y1, x2, y2, label, color, rad=0.0,
              lx=None, ly=None, ha="center"):
        a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                            mutation_scale=16, linewidth=1.8, color=color,
                            connectionstyle=f"arc3,rad={rad}")
        ax.add_patch(a)
        if lx is None: lx = (x1 + x2) / 2
        if ly is None: ly = (y1 + y2) / 2
        ax.text(lx, ly, label, ha=ha, va="center", fontsize=10.5,
                color=color, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.16", fc=PAPER, ec="none"))

    # Top horizontal pair (curved to separate labels).
    arrow(4.00, 4.45, 6.00, 4.45, "stimulates androgen synthesis",
          TEAL, rad=-0.18, ly=4.95)
    arrow(6.00, 4.15, 4.00, 4.15, "↑ androgens worsen IR",
          CORAL, rad=-0.18, ly=3.65)

    # Right vertical (theca → liver via androgens).
    arrow(7.70, 3.70, 7.70, 2.55, "↑ androgens reach liver",
          CORAL, lx=8.00, ha="left")

    # Bottom horizontal (free T circulates).
    arrow(6.00, 1.95, 4.00, 1.95, "↑ free T → adipose / muscle",
          GOLD, ly=1.45)

    # Left vertical (IR drives insulin).
    arrow(2.30, 2.55, 2.30, 3.70, "IR drives hyperinsulinemia",
          LAV, lx=2.00, ha="right")

    # Long-term risk band at the very bottom.
    risk = FancyBboxPatch((0.20, 0.10), 9.60, 0.75,
                          boxstyle="round,pad=0.06,rounding_size=0.08",
                          linewidth=1.0, edgecolor=NAVY, facecolor="#f1f5f9")
    ax.add_patch(risk)
    ax.text(0.40, 0.66, "Long-term risk in PCOS",
            fontsize=11, fontweight="bold", color=NAVY,
            ha="left", va="center")
    risks = [
        ("T2DM 3–7×", CORAL),
        ("MetS ~3×", GOLD),
        ("GDM ~2.5×", GOLD),
        ("NAFLD 2–3×", LAV),
        ("CVD ~2×", CORAL),
        ("Endom. hyper. ~2.7×", LAV),
    ]
    x = 0.40
    for text, color in risks:
        ax.text(x, 0.30, text, fontsize=10, color=color,
                fontweight="bold", ha="left", va="center")
        x += len(text) * 0.105 + 0.30

    return _save(fig, "insulin_androgen.png")


def follicular_arrest() -> Path:
    """Bio-3: Healthy vs polycystic ovary morphology."""
    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, dpi=DPI,
                             gridspec_kw=dict(wspace=0.15))
    fig.suptitle("Follicular arrest: normal vs polycystic ovarian morphology",
                 fontsize=17, fontweight="bold", color=NAVY, y=0.96, x=0.04,
                 ha="left")

    def draw_ovary(ax, title, mode):
        ax.set_xlim(-5.0, 5.0)
        ax.set_ylim(-4.0, 3.5)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=13.5, fontweight="bold",
                     color=NAVY, loc="left", pad=8)
        # Ovary outline.
        ov = mpatches.Ellipse((0, 0.8), 7.4, 4.6, linewidth=2.0,
                              edgecolor=NAVY, facecolor="#f6e9df")
        ax.add_patch(ov)
        stroma = mpatches.Ellipse((0, 0.8), 6.0, 3.7, linewidth=0,
                                  facecolor="#e9d5c2", alpha=0.55)
        ax.add_patch(stroma)
        rng = np.random.default_rng(42 if mode == "normal" else 7)
        if mode == "normal":
            for cx, cy, r in [
                (-1.2, 1.1, 0.78),
                ( 1.1, 1.6, 0.32),
                ( 0.3, 0.0, 0.28),
                (-0.5, 0.3, 0.22),
                ( 1.4, 0.3, 0.24),
                (-1.7, 0.0, 0.18),
            ]:
                ax.add_patch(mpatches.Circle((cx, cy), r,
                            facecolor="#cde7eb", edgecolor=TEAL,
                            linewidth=1.4))
            # Dominant-follicle annotation outside the ovary.
            ax.annotate("dominant\nfollicle",
                        xy=(-1.2, 1.1), xytext=(-4.5, 3.0),
                        fontsize=11, color=TEAL, fontweight="bold",
                        ha="left",
                        arrowprops=dict(arrowstyle="-",
                                        color=TEAL, lw=1.1))
            bullets = [
                "• 5–10 antral follicles",
                "• One dominant follicle matures",
                "• Ovulatory cycle proceeds",
            ]
        else:
            n = 14
            angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
            rad_a, rad_b = 2.9, 1.85
            for ang in angles:
                cx = rad_a * np.cos(ang)
                cy = 0.8 + rad_b * np.sin(ang)
                r = 0.30 + rng.uniform(-0.04, 0.04)
                ax.add_patch(mpatches.Circle((cx, cy), r,
                            facecolor="#f3d4c8", edgecolor=CORAL,
                            linewidth=1.4))
            ax.text(0, 0.8, "dense\nstroma", fontsize=11,
                    ha="center", va="center", color=CORAL,
                    fontweight="bold")
            bullets = [
                "• ≥ 12 follicles, 2–9 mm",
                "• Peripheral 'string of pearls'",
                "• No dominant follicle",
                "• Rotterdam: volume ≥ 10 mL",
            ]
        for i, b in enumerate(bullets):
            ax.text(-4.7, -2.0 - i * 0.45, b, fontsize=11, color=INK,
                    ha="left", va="top")

    draw_ovary(axes[0], "Healthy ovary (mid-follicular)", "normal")
    draw_ovary(axes[1], "Polycystic ovary morphology",    "pcos")

    fig.text(0.04, 0.03,
             "Schematic only; Rotterdam 2003 ultrasound criteria define the threshold.",
             fontsize=9, color=MUTED, ha="left")

    return _save(fig, "ovary_morphology.png")


def phenotype_venn() -> Path:
    """Bio-4: Rotterdam phenotypes Venn + prevalence bar chart."""
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    fig.suptitle("Rotterdam phenotypes A–D — heterogeneity to respect",
                 fontsize=17, fontweight="bold", color=NAVY, x=0.04, y=0.96,
                 ha="left")

    # Venn on left.
    ax = fig.add_axes([0.02, 0.12, 0.50, 0.74])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")

    r = 2.4
    for cx, cy, color in [(4.0, 6.2, TEAL), (6.0, 6.2, CORAL),
                          (5.0, 4.2, GOLD)]:
        ax.add_patch(mpatches.Circle((cx, cy), r, facecolor=color,
                                     edgecolor=color, alpha=0.22,
                                     linewidth=1.8))

    # Circle labels outside the diagram.
    ax.text(1.3, 8.7, "Hyperandrogenism", fontsize=12, color=TEAL,
            fontweight="bold", ha="left")
    ax.text(7.0, 8.7, "Ovulatory dysfn", fontsize=12, color=CORAL,
            fontweight="bold", ha="left")
    ax.text(5.0, 1.0, "Polycystic morphology", fontsize=12, color=GOLD,
            fontweight="bold", ha="center")

    # Phenotype tags inside regions with clear vertical separation.
    def tag(cx, cy, label, sub):
        ax.text(cx, cy + 0.20, label, fontsize=16, fontweight="bold",
                color=NAVY, ha="center")
        ax.text(cx, cy - 0.42, sub, fontsize=9.5, color=INK, ha="center")

    tag(5.0, 7.55, "B",  "H+O · ~10%")
    tag(5.0, 5.50, "A",  "H+O+P · ~50%")
    tag(3.30, 4.80, "C", "H+P · ~25%")
    tag(6.70, 4.80, "D", "O+P · ~15%")

    # Bar chart on the right.
    bax = fig.add_axes([0.59, 0.22, 0.37, 0.62])
    phenos = ["A: H+O+P", "B: H+O", "C: H+P", "D: O+P"]
    prev = [50, 10, 25, 15]
    colors = [NAVY, TEAL, CORAL, GOLD]
    y = np.arange(len(phenos))
    bax.barh(y, prev, color=colors, edgecolor=NAVY, linewidth=0.5)
    for yi, v in enumerate(prev):
        bax.text(v + 1.5, yi, f"{v}%", va="center", fontsize=11.5,
                 color=INK, fontweight="bold")
    bax.set_yticks(y)
    bax.set_yticklabels(phenos, fontsize=11)
    bax.invert_yaxis()
    bax.set_xlim(0, 65)
    bax.set_xlabel("Prevalence (%)", fontsize=10.5, color=INK)
    bax.spines["top"].set_visible(False)
    bax.spines["right"].set_visible(False)
    bax.set_title("Phenotype prevalence (Lizneva 2016)",
                  fontsize=11.5, fontweight="bold", color=NAVY,
                  loc="left", pad=6)
    bax.tick_params(axis="x", labelsize=9.5)

    fig.text(0.04, 0.03,
             "Phenotype B (no PCOM on ultrasound) often presents without follicle "
             "counts — caught by the screening tier without ultrasound.",
             fontsize=9, color=MUTED, ha="left")

    return _save(fig, "phenotype_venn.png")


def single_cell_gene_grid() -> Path:
    """Bio-5: 5-column grid of PCOS-linked genes from single-cell overlap."""
    df = pd.read_csv("outputs/metrics/single_cell_pcos_gene_overlap.csv")

    def pick(keyword) -> list[str]:
        if isinstance(keyword, str):
            keyword = [keyword]
        out = []
        for _, row in df.iterrows():
            ctx = str(row["literature_context"]).lower()
            if any(k.lower() in ctx for k in keyword):
                out.append(row["gene_symbol"])
        return out

    columns = [
        ("Steroidogenesis",
         ["Steroid biosynthesis", "Steroidogenesis", "Aromatase", "AMH",
          "Androgen biosynthesis", "Steroidogenic"]),
        ("Androgen sig.",
         ["5-alpha reductase", "androgen", "Aromatase"]),
        ("Insulin axis",
         ["Insulin"]),
        ("Follicular dev.",
         ["FSH receptor", "LH/CG receptor", "Granulosa",
          "AMH receptor", "AMH"]),
        ("GWAS loci",
         ["GWAS"]),
    ]

    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    fig.suptitle("Single-cell expression overlap with PCOS gene programs",
                 fontsize=17, fontweight="bold", color=NAVY, x=0.04, y=0.96,
                 ha="left")

    n_cols = len(columns)
    palette = [TEAL, CORAL, GOLD, LAV, GREEN]
    left_margin = 0.04
    right_margin = 0.02
    avail = 1.0 - left_margin - right_margin
    col_w = avail / n_cols
    for ci, (title, kw) in enumerate(columns):
        ax = fig.add_axes([left_margin + ci * col_w + 0.006, 0.10,
                           col_w - 0.012, 0.78])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        color = palette[ci]
        # Header.
        ax.add_patch(FancyBboxPatch((0.02, 0.88), 0.96, 0.10,
                                    boxstyle="round,pad=0.02,rounding_size=0.02",
                                    facecolor=color, edgecolor=color))
        ax.text(0.5, 0.93, title, ha="center", va="center",
                fontsize=12, fontweight="bold", color="white")

        genes = pick(kw)
        seen, ordered = set(), []
        for g in genes:
            if g not in seen:
                ordered.append(g)
                seen.add(g)
        if not ordered:
            ordered = ["—"]
        n = len(ordered)
        h = min(0.085, 0.78 / max(n, 1))
        for gi, g in enumerate(ordered):
            y = 0.84 - (gi + 1) * (h + 0.012)
            ax.add_patch(FancyBboxPatch((0.06, y), 0.88, h,
                        boxstyle="round,pad=0.02,rounding_size=0.02",
                        facecolor="white", edgecolor=color, linewidth=1.0))
            ax.text(0.5, y + h / 2, g, ha="center", va="center",
                    fontsize=11.5, color=INK, fontweight="bold")

    fig.text(0.04, 0.03,
             "Genes from outputs/metrics/single_cell_pcos_gene_overlap.csv. "
             "Biological rationale only; the diagnostic model uses tabular features.",
             fontsize=9, color=MUTED, ha="left")

    return _save(fig, "single_cell_genes.png")


def main():
    paths = [
        hpo_axis(),
        insulin_androgen_loop(),
        follicular_arrest(),
        phenotype_venn(),
        single_cell_gene_grid(),
    ]
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
