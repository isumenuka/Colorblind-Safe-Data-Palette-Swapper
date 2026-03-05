"""
Colorblind-Safe Data Palette Swapper — LoRA Training Dataset Generator
=======================================================================
Generates Multi-Image Edit Dataset pairs in the format expected by the
ModelScope / LoRA training upload interface:

    N_start_1.jpg  — Original inaccessible chart (source image 1)
    N_start_2.jpg  — A second variant/style of the same chart (source image 2)
    N_end.jpg      — The colorblind-safe target transformation
    N.txt          — Caption describing the transformation rule

Colorblind modes supported:
    • Deuteranopia  → Blue / Orange high-contrast palette
    • Protanopia    → Blue / Yellow high-contrast palette
    • Monochromacy  → High-contrast Grayscale + Pattern fills

Chart types: Pie, Bar (grouped), Line (multi-series), Scatter, Heatmap
"""

import os
import random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe
from pathlib import Path

# ---------------------------------------------------------------------------
# OUTPUT CONFIG
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("dataset_output")
OUTPUT_DIR.mkdir(exist_ok=True)

PAIRS_PER_MODE = 5           # Number of dataset pairs to generate per colorblind mode
DPI = 150                    # Image resolution (higher = better quality)
FIG_SIZE = (7, 5)            # Figure dimensions in inches
JPG_QUALITY = 95             # JPEG quality (1-100)

# ---------------------------------------------------------------------------
# COLOR PALETTES
# ---------------------------------------------------------------------------

# Standard "dangerous" palettes — heavy red/green reliance
STANDARD_PALETTES = [
    ["#E63946", "#2DC653", "#F4A261", "#A8DADC", "#1D3557"],   # Red-green dominant
    ["#FF0000", "#00FF00", "#FFFF00", "#0000FF", "#FF69B4"],   # Pure RGB danger
    ["#D62728", "#2CA02C", "#FF7F0E", "#9467BD", "#8C564B"],   # Matplotlib default
    ["#CC0000", "#00CC00", "#CCCC00", "#006699", "#CC6600"],   # Traffic-light style
    ["#B22222", "#228B22", "#DAA520", "#4169E1", "#DC143C"],   # Earth-red/green
]

# Deuteranopia-safe: Blue / Orange / High-contrast
DEUTERANOPIA_PALETTES = [
    ["#0077BB", "#EE7733", "#009988", "#CC3311", "#33BBEE"],
    ["#004488", "#DDAA33", "#BB5566", "#000000", "#AAAA00"],
    ["#1A5276", "#E67E22", "#2E86C1", "#D35400", "#154360"],
    ["#003F88", "#FCA311", "#00509D", "#E63946", "#023E8A"],
    ["#0072B2", "#E69F00", "#56B4E9", "#D55E00", "#009E73"],   # Wong palette
]

# Protanopia-safe: Blue / Yellow / Purple distinctions
PROTANOPIA_PALETTES = [
    ["#0077BB", "#EECC66", "#EE99AA", "#BBBBBB", "#44BB99"],
    ["#332288", "#DDCC77", "#88CCEE", "#882255", "#117733"],
    ["#0050A0", "#FFD700", "#5DA5DA", "#B276B2", "#60BD68"],
    ["#1B4F72", "#F1C40F", "#154360", "#6C3483", "#1A5276"],
    ["#003049", "#FCBF49", "#D62828", "#F77F00", "#EAE2B7"],
]

# Monochromacy-safe: Grayscale values well-spaced in luminance
MONOCHROMACY_PALETTES = [
    ["#000000", "#404040", "#808080", "#BFBFBF", "#FFFFFF"],
    ["#1A1A1A", "#4D4D4D", "#808080", "#B3B3B3", "#E6E6E6"],
    ["#0D0D0D", "#3D3D3D", "#6E6E6E", "#9E9E9E", "#CFCFCF"],
    ["#111111", "#444444", "#777777", "#AAAAAA", "#DDDDDD"],
    ["#000000", "#333333", "#666666", "#999999", "#CCCCCC"],
]

# Hatch patterns for monochromacy (textures make sections distinguishable)
HATCH_PATTERNS = ["", "///", "xxx", "...", "+++", "\\\\\\", "ooo", "***"]

# ---------------------------------------------------------------------------
# CAPTION TEMPLATES
# ---------------------------------------------------------------------------

DEUTERANOPIA_CAPTIONS = [
    "Transform this data visualization to a deuteranopia-safe blue and orange color palette, preserving all chart geometry, labels, and data values exactly.",
    "Recolor this chart to a high-contrast deuteranopia-accessible blue-orange palette. Do not alter any text, shapes, or data points.",
    "Apply a deuteranopia-safe color transformation: replace red-green conflicting colors with distinguishable blue and orange tones while keeping the chart structure intact.",
    "Convert the color palette of this data visualization to be safe for deuteranopia (red-green colorblindness) using a blue and orange scheme.",
    "Edit the chart colors to a deuteranopia-friendly palette (blue/orange high contrast) without changing any labels, data, or layout.",
]

PROTANOPIA_CAPTIONS = [
    "Transform this data visualization to a protanopia-safe blue and yellow color palette, preserving all chart geometry, labels, and data values exactly.",
    "Recolor this chart to a high-contrast protanopia-accessible blue-yellow palette. Do not alter any text, shapes, or data points.",
    "Apply a protanopia-safe color transformation: replace conflicting colors with distinguishable blue and yellow tones while keeping the chart structure intact.",
    "Convert the color palette of this data visualization to be safe for protanopia using a blue and yellow scheme.",
    "Edit the chart colors to a protanopia-friendly palette (blue/yellow high contrast) without changing any labels, data, or layout.",
]

MONOCHROMACY_CAPTIONS = [
    "Transform this data visualization to a high-contrast grayscale palette with distinct cross-hatching and pattern fills for each section, preserving all chart geometry and labels.",
    "Convert this chart to a monochromacy-safe design: apply a well-spaced grayscale palette with unique hatch patterns (lines, dots, crosses) so each segment is distinguishable without color.",
    "Recolor this chart to accessible grayscale and add distinct fill textures (hatching, stippling, or crosshatching) to each data region for monochromacy accessibility.",
    "Apply a total colorblindness (monochromacy) safe transformation: render all chart areas in high-contrast grayscale with distinguishable pattern fills for each category.",
    "Edit this data visualization for monochromacy accessibility by converting to a high-contrast grayscale palette with unique hatch patterns per data series.",
]

# ---------------------------------------------------------------------------
# RANDOM DATA GENERATORS
# ---------------------------------------------------------------------------

CHART_LABELS_POOL = [
    ["Healthy", "At Risk", "Critical", "Stable", "Unknown"],
    ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E"],
    ["Q1", "Q2", "Q3", "Q4", "YTD"],
    ["Group 1", "Group 2", "Group 3", "Group 4", "Group 5"],
    ["Low", "Medium", "High", "Very High", "Extreme"],
    ["Category A", "Category B", "Category C", "Category D", "Category E"],
    ["North", "South", "East", "West", "Central"],
    ["Jan–Mar", "Apr–Jun", "Jul–Sep", "Oct–Dec", "Full Year"],
]

def random_labels(n=5):
    pool = random.choice(CHART_LABELS_POOL)
    return pool[:n]

def random_values(n=5, low=5, high=100):
    return [random.randint(low, high) for _ in range(n)]

def random_title():
    subjects = ["Bone Density", "Risk Score", "Patient Distribution", "Resource Allocation",
                "Diagnostic Results", "Screening Outcomes", "Performance Metrics", "Survey Responses"]
    suffixes = ["Analysis", "Overview", "by Region", "by Category", "Summary", "Breakdown", "Report"]
    return f"{random.choice(subjects)} {random.choice(suffixes)}"

# ---------------------------------------------------------------------------
# CHART DRAWING FUNCTIONS
# ---------------------------------------------------------------------------

def apply_style(ax, fig):
    """Applies a clean, professional background style to any axes."""
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#FFFFFF")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.tick_params(colors="#444444", labelsize=9)
    ax.title.set_color("#222222")
    ax.title.set_fontsize(12)
    ax.title.set_fontweight("bold")


def draw_pie(ax, fig, colors, hatches=None, title=""):
    n = random.randint(3, 5)
    labels = random_labels(n)
    values = random_values(n, 10, 80)
    wedge_props = {"linewidth": 1.5, "edgecolor": "white"}

    if hatches:
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, colors=colors[:n],
            autopct="%1.1f%%", startangle=140,
            wedgeprops=wedge_props, pctdistance=0.75
        )
        for wedge, h in zip(wedges, hatches[:n]):
            wedge.set_hatch(h)
    else:
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, colors=colors[:n],
            autopct="%1.1f%%", startangle=140,
            wedgeprops=wedge_props, pctdistance=0.75
        )

    for autotext in autotexts:
        autotext.set_fontsize(8)
        autotext.set_color("#222222")
    ax.set_title(title or random_title())
    fig.patch.set_facecolor("#F8F9FA")


def draw_bar(ax, fig, colors, hatches=None, title=""):
    n = random.randint(3, 5)
    labels = random_labels(n)
    values1 = random_values(n, 10, 80)
    values2 = random_values(n, 10, 80)
    x = np.arange(n)
    w = 0.38

    bars1 = ax.bar(x - w/2, values1, w, color=colors[0], label="Series A",
                   edgecolor="white", linewidth=1)
    bars2 = ax.bar(x + w/2, values2, w, color=colors[1], label="Series B",
                   edgecolor="white", linewidth=1)

    if hatches:
        for bar in bars1:
            bar.set_hatch(hatches[0])
        for bar in bars2:
            bar.set_hatch(hatches[1] if len(hatches) > 1 else hatches[0])

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Value", fontsize=9)
    ax.legend(fontsize=8, framealpha=0.7)
    ax.set_title(title or random_title())
    ax.set_ylim(0, max(max(values1), max(values2)) * 1.25)
    apply_style(ax, fig)


def draw_line(ax, fig, colors, hatches=None, title=""):
    n_points = random.randint(6, 10)
    n_series = random.randint(2, 4)
    x = list(range(1, n_points + 1))
    markers = ["o", "s", "^", "D"]
    series_names = random_labels(n_series)

    for i in range(n_series):
        y = np.cumsum(np.random.randint(-10, 15, n_points)) + random.randint(20, 60)
        ax.plot(x, y, color=colors[i % len(colors)], marker=markers[i % 4],
                label=series_names[i], linewidth=2, markersize=6)

    ax.set_xlabel("Time Point", fontsize=9)
    ax.set_ylabel("Measurement", fontsize=9)
    ax.legend(fontsize=8, framealpha=0.7)
    ax.set_title(title or random_title())
    ax.grid(True, alpha=0.3, linestyle="--")
    apply_style(ax, fig)


def draw_scatter(ax, fig, colors, hatches=None, title=""):
    n_groups = random.randint(2, 4)
    group_names = random_labels(n_groups)
    markers = ["o", "s", "^", "D"]

    for i in range(n_groups):
        n_pts = random.randint(15, 35)
        cx, cy = random.uniform(20, 80), random.uniform(20, 80)
        x = np.random.normal(cx, random.uniform(5, 12), n_pts)
        y = np.random.normal(cy, random.uniform(5, 12), n_pts)
        ax.scatter(x, y, color=colors[i % len(colors)], label=group_names[i],
                   alpha=0.75, edgecolors="white", linewidths=0.5,
                   s=random.randint(40, 90), marker=markers[i % 4])

    ax.set_xlabel("Variable X", fontsize=9)
    ax.set_ylabel("Variable Y", fontsize=9)
    ax.legend(fontsize=8, framealpha=0.7)
    ax.set_title(title or random_title())
    ax.grid(True, alpha=0.3, linestyle="--")
    apply_style(ax, fig)


def draw_heatmap(ax, fig, colors, hatches=None, title=""):
    n_rows = random.randint(4, 6)
    n_cols = random.randint(4, 6)
    data = np.random.randint(0, 100, (n_rows, n_cols))
    row_labels = [f"R{i+1}" for i in range(n_rows)]
    col_labels = [f"C{i+1}" for i in range(n_cols)]

    # Build a colormap from the provided palette colors (low → high)
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("cb_heatmap", [colors[0], colors[2] if len(colors) > 2 else colors[-1]])

    im = ax.imshow(data, cmap=cmap, aspect="auto")
    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(col_labels, fontsize=8)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(row_labels, fontsize=8)

    for r in range(n_rows):
        for c in range(n_cols):
            ax.text(c, r, str(data[r, c]), ha="center", va="center",
                    fontsize=7, color="white" if data[r, c] < 50 else "black")

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title(title or random_title())
    fig.patch.set_facecolor("#F8F9FA")


CHART_DRAWERS = [draw_pie, draw_bar, draw_line, draw_scatter, draw_heatmap]

# ---------------------------------------------------------------------------
# SAVE FIGURE HELPER
# ---------------------------------------------------------------------------

def save_fig(fig, path: Path):
    fig.savefig(str(path), dpi=DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor(), format="jpeg",
                pil_kwargs={"quality": JPG_QUALITY, "optimize": True})
    plt.close(fig)


# ---------------------------------------------------------------------------
# DATASET PAIR GENERATOR
# ---------------------------------------------------------------------------

def generate_pair(pair_index: int, mode: str):
    """
    Generates one complete Multi-Image Edit Dataset pair:
        {pair_index}_start_1.jpg  — Original chart (standard/inaccessible palette)
        {pair_index}_start_2.jpg  — Same chart type with another inaccessible variant
        {pair_index}_end.jpg      — Transformed chart (colorblind-safe target)
        {pair_index}.txt          — Caption describing the edit
    """
    # --- Select chart type and title ---
    drawer = random.choice(CHART_DRAWERS)
    title = random_title()

    # --- Select palettes ---
    std_palette_1 = random.choice(STANDARD_PALETTES)
    # Slightly different second standard palette for start_2 variation
    std_palette_2 = random.choice([p for p in STANDARD_PALETTES if p != std_palette_1])

    if mode == "deuteranopia":
        safe_palette = random.choice(DEUTERANOPIA_PALETTES)
        caption = random.choice(DEUTERANOPIA_CAPTIONS)
        hatches = None
    elif mode == "protanopia":
        safe_palette = random.choice(PROTANOPIA_PALETTES)
        caption = random.choice(PROTANOPIA_CAPTIONS)
        hatches = None
    elif mode == "monochromacy":
        safe_palette = random.choice(MONOCHROMACY_PALETTES)
        caption = random.choice(MONOCHROMACY_CAPTIONS)
        # Assign distinct hatch patterns for monochromacy
        pattern_set = random.sample(HATCH_PATTERNS, min(5, len(HATCH_PATTERNS)))
        hatches = pattern_set
    else:
        raise ValueError(f"Unknown mode: {mode}")

    # --- Draw start_1 (original, inaccessible) ---
    fig1, ax1 = plt.subplots(figsize=FIG_SIZE)
    drawer(ax1, fig1, std_palette_1, hatches=None, title=title)
    path_start1 = OUTPUT_DIR / f"{pair_index}_start_1.jpg"
    save_fig(fig1, path_start1)

    # --- Draw start_2 (second inaccessible variant — same chart type, different data seed) ---
    fig2, ax2 = plt.subplots(figsize=FIG_SIZE)
    drawer(ax2, fig2, std_palette_2, hatches=None, title=title)
    path_start2 = OUTPUT_DIR / f"{pair_index}_start_2.jpg"
    save_fig(fig2, path_start2)

    # --- Draw end (colorblind-safe target) ---
    fig3, ax3 = plt.subplots(figsize=FIG_SIZE)
    drawer(ax3, fig3, safe_palette, hatches=hatches, title=title)
    path_end = OUTPUT_DIR / f"{pair_index}_end.jpg"
    save_fig(fig3, path_end)

    # --- Write caption ---
    path_txt = OUTPUT_DIR / f"{pair_index}.txt"
    path_txt.write_text(caption, encoding="utf-8")

    print(f"  ✓ Pair {pair_index:03d} [{mode:>12s}] — {title}")
    return pair_index


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("=" * 62)
    print("  Colorblind-Safe Data Palette Swapper")
    print("  LoRA Multi-Image Edit Dataset Generator")
    print("=" * 62)
    print(f"  Output directory : {OUTPUT_DIR.resolve()}")
    print(f"  Pairs per mode   : {PAIRS_PER_MODE}")
    print(f"  Total pairs      : {PAIRS_PER_MODE * 3}")
    print("-" * 62)

    modes = [
        ("deuteranopia",  PAIRS_PER_MODE),
        ("protanopia",    PAIRS_PER_MODE),
        ("monochromacy",  PAIRS_PER_MODE),
    ]

    pair_index = 1
    for mode, count in modes:
        print(f"\n[{mode.upper()}]")
        for _ in range(count):
            generate_pair(pair_index, mode)
            pair_index += 1

    total = pair_index - 1
    print("\n" + "=" * 62)
    print(f"  Done! Generated {total} dataset pairs.")
    print(f"  Files: {total * 4} total  ({total} × _start_1.jpg, _start_2.jpg, _end.jpg, .txt)")
    print(f"  Location: {OUTPUT_DIR.resolve()}")
    print("=" * 62)


if __name__ == "__main__":
    random.seed(42)          # Remove for fully random generation each run
    np.random.seed(42)
    main()