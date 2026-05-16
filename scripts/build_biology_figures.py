"""Generate biology schematic figures for the PCOS Pathfinder pptx deck.

Each figure is a single, generously-spaced panel with no overlapping labels.
All figures are sized <= 1800x1100 px to stay well under image-handling limits
and to align comfortably inside a 16:9 slide's body area.
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

FIGSIZE = (14.0, 8.0)  # 16:9.14 — keeps room for a wide schematic
DPI = 110  # ~1540x880 px

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 13,
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
                pad_inches=0.30)
    plt.close(fig)
    return path


def _node(ax, cx, cy, w, h, label, sub, color, bg):
    box = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.12,rounding_size=0.20",
        linewidth=1.8, edgecolor=color, facecolor=bg,
    )
    ax.add_patch(box)
    ax.text(cx, cy + 0.30, label, ha="center", va="center",
            fontsize=16, fontweight="bold", color=color)
    ax.text(cx, cy - 0.45, sub, ha="center", va="center",
            fontsize=12, color=MUTED)


def hpo_axis() -> Path:
    """Slide bio-1: HPO axis schematic — single panel."""
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.set_title(
        "HPO axis: where PCOS hyperandrogenism arises",
        fontsize=22, fontweight="bold", color=NAVY, loc="left", pad=14,
    )

    # Three-stage column on the left.
    _node(ax, 2.3, 7.4, 3.4, 1.4, "Hypothalamus", "GnRH pulses",   TEAL,  SOFT_TEAL)
    _node(ax, 2.3, 4.5, 3.4, 1.4, "Pituitary",    "LH / FSH",      LAV,   SOFT_LAV)
    _node(ax, 2.3, 1.5, 3.4, 1.4, "Ovary",        "Theca + granulosa", CORAL, SOFT_CORAL)

    def arrow(x1, y1, x2, y2, label, color, side="right"):
        a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                            mutation_scale=22, linewidth=2.4, color=color)
        ax.add_patch(a)
        lx = x1 + 0.25
        ax.text(lx, (y1 + y2) / 2, label, ha="left", va="center",
                fontsize=13, color=color, fontweight="bold")

    arrow(2.3, 6.7, 2.3, 5.2, "GnRH pulse", TEAL)
    arrow(2.3, 3.8, 2.3, 2.2, "↑ LH (LH:FSH ratio rises)", LAV)

    # Right-side "In PCOS" panel — wider so bullets never wrap.
    panel = FancyBboxPatch((6.5, 1.0), 7.0, 7.1,
                           boxstyle="round,pad=0.14,rounding_size=0.18",
                           linewidth=1.6, edgecolor=NAVY, facecolor="#f1f5f9")
    ax.add_patch(panel)
    ax.text(6.85, 7.6, "In PCOS", fontsize=18, fontweight="bold",
            color=NAVY, ha="left", va="top")

    bullets = [
        "Faster GnRH pulse frequency at the hypothalamus",
        "↑ LH relative to FSH (often LH:FSH ≥ 2)",
        "↑ Theca-cell androgen output (testosterone, androstenedione)",
        "↓ Aromatization of androgens to estradiol",
        "Follicular arrest at ~2–8 mm; no dominant follicle",
        "Clinical: hirsutism, acne, oligo-ovulation",
    ]
    for i, b in enumerate(bullets):
        y = 6.7 - i * 0.85
        ax.text(6.95, y, "•", fontsize=15, color=NAVY, fontweight="bold",
                ha="left", va="center")
        ax.text(7.30, y, b, fontsize=13.5, color=INK, ha="left", va="center")

    # Footer note inside the figure.
    ax.text(0.10, 0.10,
            "Schematic only. Reference: ESHRE/Rotterdam consensus on PCOS pathophysiology.",
            fontsize=10, color=MUTED, ha="left", va="bottom")

    return _save(fig, "hpo_axis.png")


def insulin_androgen_loop() -> Path:
    """Slide bio-2: insulin–androgen feedback loop, single panel."""
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.set_title("Insulin resistance amplifies ovarian androgen output",
                 fontsize=22, fontweight="bold", color=NAVY, loc="left", pad=14)

    # Four nodes laid out as a wide rectangle with generous spacing.
    _node(ax, 3.2, 6.6, 4.6, 1.7, "Hyperinsulinemia", "from peripheral IR",
          TEAL, SOFT_TEAL)
    _node(ax, 10.8, 6.6, 4.6, 1.7, "Ovarian theca", "↑ androgen synthesis",
          CORAL, SOFT_CORAL)
    _node(ax, 10.8, 2.6, 4.6, 1.7, "Liver",
          "↓ SHBG → ↑ free testosterone", GOLD, SOFT_GOLD)
    _node(ax, 3.2, 2.6, 4.6, 1.7, "Adipose / muscle",
          "insulin resistance", LAV, SOFT_LAV)

    def arrow(x1, y1, x2, y2, label, color, rad=0.0,
              lx=None, ly=None, ha="center"):
        a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                            mutation_scale=22, linewidth=2.4, color=color,
                            connectionstyle=f"arc3,rad={rad}")
        ax.add_patch(a)
        if lx is None: lx = (x1 + x2) / 2
        if ly is None: ly = (y1 + y2) / 2
        ax.text(lx, ly, label, ha=ha, va="center", fontsize=12.5,
                color=color, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.22", fc=PAPER, ec="none"))

    # Top horizontal arrows (slight curve to separate the two labels).
    arrow(5.55, 6.85, 8.45, 6.85, "stimulates androgen synthesis",
          TEAL, rad=-0.16, ly=7.55)
    arrow(8.45, 6.35, 5.55, 6.35, "↑ androgens worsen insulin resistance",
          CORAL, rad=-0.16, ly=5.65)

    # Right vertical (theca → liver via androgens). One label only — the
    # Liver node subtitle already states the SHBG → free-T effect.
    arrow(10.8, 5.7, 10.8, 3.5, "↑ androgens reach liver",
          CORAL, lx=11.2, ha="left", ly=4.6)

    # Bottom horizontal (free T circulates back).
    arrow(8.45, 2.6, 5.55, 2.6, "↑ free T → adipose / muscle",
          GOLD, ly=1.85)

    # Left vertical (IR drives insulin up).
    arrow(3.2, 3.5, 3.2, 5.7, "IR drives hyperinsulinemia",
          LAV, lx=1.4, ha="right")

    # Long-term risk footer band.
    risk = FancyBboxPatch((0.40, 0.20), 13.2, 0.95,
                          boxstyle="round,pad=0.10,rounding_size=0.10",
                          linewidth=1.0, edgecolor=NAVY, facecolor="#f1f5f9")
    ax.add_patch(risk)
    ax.text(0.70, 0.95, "Long-term risk in PCOS",
            fontsize=12, fontweight="bold", color=NAVY,
            ha="left", va="center")
    multipliers = [
        ("T2DM 3–7×",   CORAL),
        ("Metabolic syndrome ~3×", GOLD),
        ("GDM ~2.5×",    GOLD),
        ("NAFLD 2–3×",   LAV),
        ("CVD ~2×",      CORAL),
        ("Endometrial hyperplasia ~2.7×", LAV),
    ]
    x = 4.30
    for text, color in multipliers:
        ax.text(x, 0.55, text, fontsize=11.5, color=color,
                fontweight="bold", ha="left", va="center")
        x += len(text) * 0.13 + 0.30

    return _save(fig, "insulin_androgen.png")


def follicular_arrest() -> Path:
    """Slide bio-3: Normal vs polycystic ovary morphology — cleanly laid out."""
    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, dpi=DPI,
                             gridspec_kw=dict(wspace=0.18))
    fig.suptitle("Follicular arrest: normal vs. polycystic ovarian morphology",
                 fontsize=22, fontweight="bold", color=NAVY, y=0.97, x=0.06,
                 ha="left")

    def draw_ovary(ax, title, mode):
        ax.set_xlim(-5.0, 5.0)
        ax.set_ylim(-5.0, 4.0)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=16, fontweight="bold",
                     color=NAVY, loc="left", pad=14)
        # Ovary outline.
        ov = mpatches.Ellipse((0, 1.0), 8.0, 5.4, linewidth=2.4,
                              edgecolor=NAVY, facecolor="#f6e9df")
        ax.add_patch(ov)
        stroma = mpatches.Ellipse((0, 1.0), 6.5, 4.2, linewidth=0,
                                  facecolor="#e9d5c2", alpha=0.55)
        ax.add_patch(stroma)
        rng = np.random.default_rng(42 if mode == "normal" else 7)
        if mode == "normal":
            follicles = [
                (-1.4, 1.4, 0.85, True),
                ( 1.2, 1.9, 0.35, False),
                ( 0.4, 0.0, 0.30, False),
                (-0.6, 0.4, 0.22, False),
                ( 1.6, 0.4, 0.25, False),
                (-2.0, 0.2, 0.18, False),
            ]
            for cx, cy, r, _ in follicles:
                ax.add_patch(mpatches.Circle((cx, cy), r,
                            facecolor="#cde7eb", edgecolor=TEAL, linewidth=1.6))
            # "dominant follicle" label OUTSIDE the ovary to avoid overlap.
            ax.annotate("dominant follicle",
                        xy=(-1.4, 1.4), xytext=(-4.6, 3.4),
                        fontsize=11.5, color=TEAL, fontweight="bold",
                        arrowprops=dict(arrowstyle="-",
                                        color=TEAL, lw=1.2))
            bullets = [
                "• 5–10 antral follicles",
                "• One dominant follicle matures",
                "• Ovulatory cycle proceeds",
            ]
        else:
            n = 14
            angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
            rad_a, rad_b = 3.2, 2.05
            for ang in angles:
                cx = rad_a * np.cos(ang)
                cy = 1.0 + rad_b * np.sin(ang)
                r = 0.34 + rng.uniform(-0.05, 0.05)
                ax.add_patch(mpatches.Circle((cx, cy), r,
                            facecolor="#f3d4c8", edgecolor=CORAL, linewidth=1.6))
            ax.text(0, 1.0, "dense\nstroma", fontsize=12,
                    ha="center", va="center", color=CORAL, fontweight="bold")
            bullets = [
                "• ≥ 12 follicles, 2–9 mm",
                "• Peripheral 'string of pearls' pattern",
                "• Arrested growth; no dominant follicle",
                "• Rotterdam: ovarian volume ≥ 10 mL",
            ]
        # Bullet block sits well below the ovary (ovary bottom is at y=-1.7).
        for i, b in enumerate(bullets):
            ax.text(-4.7, -2.4 - i * 0.55, b, fontsize=12.5, color=INK,
                    ha="left", va="top")

    draw_ovary(axes[0], "Healthy ovary (mid-follicular)", "normal")
    draw_ovary(axes[1], "Polycystic ovary morphology",    "pcos")

    fig.text(0.06, 0.02,
             "Schematic only; Rotterdam 2003 ultrasound criteria define the threshold "
             "for polycystic ovarian morphology.",
             fontsize=10.5, color=MUTED, ha="left")

    return _save(fig, "ovary_morphology.png")


def phenotype_venn() -> Path:
    """Slide bio-4: Rotterdam phenotypes A–D — Venn + cleanly separated bar."""
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    # Reserve top room for the suptitle, more vertical room for the bars.
    fig.suptitle("Rotterdam phenotypes A–D — heterogeneity that the tiered workflow must respect",
                 fontsize=20, fontweight="bold", color=NAVY, x=0.06, y=0.96,
                 ha="left")

    # Left: Venn.
    ax = fig.add_axes([0.04, 0.10, 0.50, 0.78])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")

    r = 2.4
    centers = {
        "H": (4.0, 6.2, TEAL),
        "O": (6.0, 6.2, CORAL),
        "P": (5.0, 4.2, GOLD),
    }
    for key, (cx, cy, color) in centers.items():
        ax.add_patch(mpatches.Circle((cx, cy), r, facecolor=color, edgecolor=color,
                                     alpha=0.22, linewidth=2.2))

    # Circle labels OUTSIDE the diagram.
    ax.text(1.6, 8.6, "Hyperandrogenism", fontsize=14, color=TEAL,
            fontweight="bold", ha="left")
    ax.text(7.4, 8.6, "Ovulatory dysfunction", fontsize=14, color=CORAL,
            fontweight="bold", ha="left")
    ax.text(5.0, 1.2, "Polycystic ovarian morphology", fontsize=14, color=GOLD,
            fontweight="bold", ha="center")

    # Phenotype tags inside the regions with clear vertical separation.
    def tag(cx, cy, label, sub):
        ax.text(cx, cy + 0.20, label, fontsize=18, fontweight="bold",
                color=NAVY, ha="center")
        ax.text(cx, cy - 0.42, sub, fontsize=10.5, color=INK, ha="center")

    tag(5.0, 7.45, "B",  "H + O · ~10%")        # H ∩ O only
    tag(5.0, 5.50, "A",  "H + O + P · ~50%")    # triple intersection
    tag(3.40, 4.80, "C", "H + P · ~25%")        # H ∩ P only
    tag(6.60, 4.80, "D", "O + P · ~15%")        # O ∩ P only

    # Right: bar chart, with its own padded axes (no clash with footer).
    bax = fig.add_axes([0.60, 0.22, 0.36, 0.66])
    phenos = ["A: H+O+P", "B: H+O", "C: H+P", "D: O+P"]
    prev = [50, 10, 25, 15]
    colors = [NAVY, TEAL, CORAL, GOLD]
    y = np.arange(len(phenos))
    bax.barh(y, prev, color=colors, edgecolor=NAVY, linewidth=0.6)
    for yi, v in enumerate(prev):
        bax.text(v + 1.0, yi, f"{v}%", va="center", fontsize=12.5,
                 color=INK, fontweight="bold")
    bax.set_yticks(y)
    bax.set_yticklabels(phenos, fontsize=12)
    bax.invert_yaxis()
    bax.set_xlim(0, 65)
    bax.set_xlabel("Prevalence among PCOS cases (%)", fontsize=11.5, color=INK)
    bax.spines["top"].set_visible(False)
    bax.spines["right"].set_visible(False)
    bax.set_title("Phenotype prevalence (Lizneva 2016)",
                  fontsize=13, fontweight="bold", color=NAVY,
                  loc="left", pad=8)

    fig.text(0.04, 0.04,
             "Why it matters: phenotype B (no PCOM on ultrasound) and lean PCOS often present without follicle counts — "
             "the screening tier catches them; the enhanced tier refines with labs.",
             fontsize=10.5, color=MUTED, ha="left", wrap=True)

    return _save(fig, "phenotype_venn.png")


def single_cell_gene_grid() -> Path:
    """Slide bio-5: 5-column grid of PCOS-linked genes."""
    df = pd.read_csv("outputs/metrics/single_cell_pcos_gene_overlap.csv")

    def pick(keyword) -> list[str]:
        if isinstance(keyword, str): keyword = [keyword]
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
        ("Androgen signalling",
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
                 fontsize=22, fontweight="bold", color=NAVY, x=0.06, y=0.96,
                 ha="left")

    n_cols = len(columns)
    palette = [TEAL, CORAL, GOLD, LAV, GREEN]
    left_margin = 0.06
    right_margin = 0.04
    avail = 1.0 - left_margin - right_margin
    col_w = avail / n_cols
    for ci, (title, kw) in enumerate(columns):
        ax = fig.add_axes([left_margin + ci * col_w + 0.008, 0.10,
                           col_w - 0.018, 0.80])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        color = palette[ci]
        ax.add_patch(FancyBboxPatch((0.02, 0.88), 0.96, 0.10,
                                    boxstyle="round,pad=0.02,rounding_size=0.02",
                                    facecolor=color, edgecolor=color))
        ax.text(0.5, 0.93, title, ha="center", va="center",
                fontsize=14, fontweight="bold", color="white")
        genes = pick(kw)
        seen, ordered = set(), []
        for g in genes:
            if g not in seen:
                ordered.append(g); seen.add(g)
        if not ordered:
            ordered = ["—"]
        n = len(ordered)
        h = min(0.085, 0.78 / max(n, 1))
        for gi, g in enumerate(ordered):
            y = 0.84 - (gi + 1) * (h + 0.012)
            ax.add_patch(FancyBboxPatch((0.06, y), 0.88, h,
                        boxstyle="round,pad=0.02,rounding_size=0.02",
                        facecolor="white", edgecolor=color, linewidth=1.1))
            ax.text(0.5, y + h / 2, g, ha="center", va="center",
                    fontsize=12, color=INK, fontweight="bold")

    fig.text(0.06, 0.03,
             "Genes from outputs/metrics/single_cell_pcos_gene_overlap.csv. "
             "Biological rationale only — the diagnostic model uses tabular clinical features.",
             fontsize=10.5, color=MUTED, ha="left")

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
