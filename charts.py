"""
charts.py — Flat, solid-color chart drawing functions for LoRA dataset generation.

CRITICAL RULES (enforced throughout):
  • FLAT ONLY — no 3D effects, no drop shadows, no gradients.
    Flat solid fills are the only thing the LoRA needs to learn to recolor.
  • SEEDED DRAWING — every drawer receives an explicit `rng` (numpy) and
    `rng_py` (Python random.Random) so that start_1 and end are drawn with
    the EXACT same random data → pixel-perfect identical geometry.
  • 1024×1024 — caller is responsible for figure size; charts fill the axes.
  • CONTRAST-AWARE TEXT — uses WCAG luminance to pick white/dark text on
    every colored background element independently.
"""
import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# WCAG CONTRAST HELPER
# ---------------------------------------------------------------------------
def text_color_for_bg(hex_color: str) -> str:
    """Returns white or near-black for maximum contrast against hex_color."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    L = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    return "#FFFFFF" if L < 0.179 else "#111111"


def rgba_to_hex(rgba) -> str:
    r, g, b = int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)
    return f"#{r:02X}{g:02X}{b:02X}"


# ---------------------------------------------------------------------------
# SHARED STYLE — clean, flat background
# ---------------------------------------------------------------------------
def _apply_flat_style(ax, fig):
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#F7F8FA")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#DDDDDD")
    ax.spines["bottom"].set_color("#DDDDDD")
    ax.tick_params(colors="#555555", labelsize=11)
    ax.title.set_color("#1A1A1A")
    ax.title.set_fontsize(15)
    ax.title.set_fontweight("bold")


# ---------------------------------------------------------------------------
# DATA POOL HELPERS  (seeded — must be called with rng / rng_py objects)
# ---------------------------------------------------------------------------
LABEL_POOLS = [
    ["Healthy", "At Risk", "Critical", "Stable", "Unknown"],
    ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E"],
    ["Q1", "Q2", "Q3", "Q4", "YTD"],
    ["Group 1", "Group 2", "Group 3", "Group 4", "Group 5"],
    ["Low", "Medium", "High", "Very High", "Extreme"],
    ["Category A", "Category B", "Category C", "Category D", "Category E"],
    ["North", "South", "East", "West", "Central"],
    ["Jan–Mar", "Apr–Jun", "Jul–Sep", "Oct–Dec", "Full Year"],
    ["Approved", "Pending", "Rejected", "On Hold", "Escalated"],
    ["Product A", "Product B", "Product C", "Product D", "Product E"],
    ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5"],
    ["Under 18", "18–34", "35–54", "55–69", "70+"],
    ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"],
    ["Mon", "Tue", "Wed", "Thu", "Fri"],
    ["2020", "2021", "2022", "2023", "2024"],
    ["Budget", "Actual", "Forecast", "Variance", "Target"],
]

TITLE_SUBJECTS = [
    "Bone Density", "Risk Score", "Patient Distribution", "Resource Allocation",
    "Diagnostic Results", "Screening Outcomes", "Performance Metrics",
    "Survey Responses", "Market Share", "Sales Volume", "Test Results",
    "Incident Rate", "Recovery Rate", "Energy Consumption", "Budget Allocation",
]
TITLE_SUFFIXES = [
    "Analysis", "Overview", "by Region", "by Category",
    "Summary", "Breakdown", "Report", "Dashboard",
]


def _labels(n, rng_py):
    pool = rng_py.choice(LABEL_POOLS)
    return pool[:n]


def _values(n, low, high, rng):
    return rng.integers(low, high + 1, n).tolist()


def _title(rng_py):
    return f"{rng_py.choice(TITLE_SUBJECTS)} {rng_py.choice(TITLE_SUFFIXES)}"


# ---------------------------------------------------------------------------
# CHART DRAWERS
# Each receives: ax, fig, colors (list[str]), hatches (list|None),
#                rng (np.random.Generator), rng_py (random.Random), title (str)
# ---------------------------------------------------------------------------

def draw_pie(ax, fig, colors, hatches, rng, rng_py, title):
    n = int(rng.integers(3, 6))
    labels = _labels(n, rng_py)
    values = _values(n, 10, 80, rng)

    wedge_props = {"linewidth": 2, "edgecolor": "#FFFFFF"}
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors[:n],
        autopct="%1.1f%%", startangle=140,
        wedgeprops=wedge_props, pctdistance=0.72,
    )
    if hatches:
        for wedge, h in zip(wedges, hatches[:n]):
            wedge.set_hatch(h)

    for wedge, autotext, label_text in zip(wedges, autotexts, texts):
        bg_hex = rgba_to_hex(wedge.get_facecolor())
        fg = text_color_for_bg(bg_hex)
        autotext.set_color(fg)
        autotext.set_fontsize(10)
        autotext.set_fontweight("bold")
        label_text.set_color("#1A1A1A")
        label_text.set_fontsize(11)

    ax.set_title(title)
    fig.patch.set_facecolor("#FFFFFF")


def draw_bar(ax, fig, colors, hatches, rng, rng_py, title):
    n = int(rng.integers(3, 6))
    labels = _labels(n, rng_py)
    v1 = _values(n, 10, 80, rng)
    v2 = _values(n, 10, 80, rng)
    x = np.arange(n)
    w = 0.38

    bars1 = ax.bar(x - w / 2, v1, w, color=colors[0], label="Series A",
                   edgecolor="#FFFFFF", linewidth=1.5)
    bars2 = ax.bar(x + w / 2, v2, w, color=colors[1], label="Series B",
                   edgecolor="#FFFFFF", linewidth=1.5)

    if hatches:
        for b in bars1: b.set_hatch(hatches[0])
        for b in bars2: b.set_hatch(hatches[1] if len(hatches) > 1 else hatches[0])

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Value", fontsize=11)
    ax.legend(fontsize=10, framealpha=0.0)
    ax.set_title(title)
    ax.set_ylim(0, max(max(v1), max(v2)) * 1.25)
    _apply_flat_style(ax, fig)


def draw_stacked_bar(ax, fig, colors, hatches, rng, rng_py, title):
    n = int(rng.integers(3, 6))
    labels = _labels(n, rng_py)
    n_series = int(rng.integers(2, 5))
    series_names = [f"Series {chr(65 + i)}" for i in range(n_series)]
    data = np.array([_values(n, 5, 50, rng) for _ in range(n_series)])
    bottom = np.zeros(n)
    x = np.arange(n)

    for i in range(n_series):
        bars = ax.bar(x, data[i], bottom=bottom,
                      color=colors[i % len(colors)],
                      label=series_names[i],
                      edgecolor="#FFFFFF", linewidth=1.5)
        if hatches:
            for b in bars:
                b.set_hatch(hatches[i % len(hatches)])
        bottom = bottom + data[i]

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Cumulative Value", fontsize=11)
    ax.legend(fontsize=10, framealpha=0.0)
    ax.set_title(title)
    _apply_flat_style(ax, fig)


def draw_line(ax, fig, colors, hatches, rng, rng_py, title):
    n_pts = int(rng.integers(6, 11))
    n_series = int(rng.integers(2, 5))
    x = list(range(1, n_pts + 1))
    markers = ["o", "s", "^", "D"]
    series_names = _labels(n_series, rng_py)

    for i in range(n_series):
        y = np.cumsum(rng.integers(-10, 15, n_pts)) + int(rng.integers(20, 61))
        ax.plot(x, y, color=colors[i % len(colors)],
                marker=markers[i % 4], label=series_names[i],
                linewidth=2.5, markersize=7,
                markeredgecolor="#FFFFFF", markeredgewidth=1)

    ax.set_xlabel("Time Point", fontsize=11)
    ax.set_ylabel("Measurement", fontsize=11)
    ax.legend(fontsize=10, framealpha=0.0)
    ax.set_title(title)
    ax.grid(True, alpha=0.25, linestyle="--", color="#AAAAAA")
    _apply_flat_style(ax, fig)


def draw_area(ax, fig, colors, hatches, rng, rng_py, title):
    n_pts = int(rng.integers(8, 15))
    n_series = int(rng.integers(2, 5))
    x = list(range(1, n_pts + 1))
    series_names = _labels(n_series, rng_py)
    base = np.zeros(n_pts)

    for i in range(n_series):
        values = np.abs(np.cumsum(rng.integers(2, 15, n_pts))) + int(rng.integers(5, 21))
        ax.fill_between(x, base, base + values,
                        color=colors[i % len(colors)],
                        alpha=0.85, label=series_names[i])
        ax.plot(x, base + values,
                color=colors[i % len(colors)],
                linewidth=1.5, alpha=0.95)
        base = base + values

    ax.set_xlabel("Time Point", fontsize=11)
    ax.set_ylabel("Value", fontsize=11)
    ax.legend(fontsize=10, framealpha=0.0)
    ax.set_title(title)
    ax.grid(True, alpha=0.2, linestyle="--", color="#AAAAAA")
    _apply_flat_style(ax, fig)


def draw_scatter(ax, fig, colors, hatches, rng, rng_py, title):
    n_groups = int(rng.integers(2, 5))
    group_names = _labels(n_groups, rng_py)
    markers = ["o", "s", "^", "D"]

    for i in range(n_groups):
        n_pts = int(rng.integers(15, 36))
        cx = float(rng.uniform(20, 80))
        cy = float(rng.uniform(20, 80))
        spread_x = float(rng.uniform(5, 12))
        spread_y = float(rng.uniform(5, 12))
        px = rng.normal(cx, spread_x, n_pts)
        py = rng.normal(cy, spread_y, n_pts)
        ax.scatter(px, py, color=colors[i % len(colors)],
                   label=group_names[i], alpha=0.80,
                   edgecolors="#FFFFFF", linewidths=0.8,
                   s=60, marker=markers[i % 4])

    ax.set_xlabel("Variable X", fontsize=11)
    ax.set_ylabel("Variable Y", fontsize=11)
    ax.legend(fontsize=10, framealpha=0.0)
    ax.set_title(title)
    ax.grid(True, alpha=0.25, linestyle="--", color="#AAAAAA")
    _apply_flat_style(ax, fig)


def draw_heatmap(ax, fig, colors, hatches, rng, rng_py, title):
    from matplotlib.colors import LinearSegmentedColormap
    n_rows = int(rng.integers(4, 7))
    n_cols = int(rng.integers(4, 7))
    data = rng.integers(0, 100, (n_rows, n_cols))
    row_labels = [f"R{i + 1}" for i in range(n_rows)]
    col_labels = [f"C{i + 1}" for i in range(n_cols)]

    # Build colormap from safe palette (dark → light)
    c_low  = colors[0]
    c_high = colors[2] if len(colors) > 2 else colors[-1]
    cmap = LinearSegmentedColormap.from_list("cb_hm", [c_low, c_high])

    im = ax.imshow(data, cmap=cmap, aspect="auto")
    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(col_labels, fontsize=9)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(row_labels, fontsize=9)

    norm = plt.Normalize(vmin=data.min(), vmax=data.max())
    for ri in range(n_rows):
        for ci in range(n_cols):
            cell_rgba = cmap(norm(data[ri, ci]))
            fg = text_color_for_bg(rgba_to_hex(cell_rgba))
            ax.text(ci, ri, str(data[ri, ci]),
                    ha="center", va="center",
                    fontsize=8, color=fg, fontweight="bold")

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title(title)
    fig.patch.set_facecolor("#FFFFFF")


# ---------------------------------------------------------------------------
# REGISTRY — used by generator to pick a random chart type
# ---------------------------------------------------------------------------
CHART_DRAWERS = [
    draw_pie,
    draw_bar,
    draw_stacked_bar,
    draw_line,
    draw_area,
    draw_scatter,
    draw_heatmap,
]
