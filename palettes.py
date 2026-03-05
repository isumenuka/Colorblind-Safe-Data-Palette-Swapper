"""
palettes.py — Color palette definitions and palette swatch (start_2) generator.

start_2 is a PALETTE KEY IMAGE — a vertical paint-chip card showing solid color
stripes only. No text, no data, no shapes. This teaches the model a strict
COLOR MAPPING RULE: "apply these exact colors to the chart from start_1."
"""
import random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from config import IMG_SIZE, DPI, FIG_INCHES, JPG_QUALITY
from pathlib import Path

# ---------------------------------------------------------------------------
# STANDARD (INACCESSIBLE) PALETTES
# Heavy red/green reliance — what the model learns to TRANSFORM away from.
# ---------------------------------------------------------------------------
STANDARD_PALETTES = [
    ["#E63946", "#2DC653", "#F4A261", "#A8DADC", "#1D3557"],
    ["#FF0000", "#00FF00", "#FFFF00", "#0000FF", "#FF69B4"],
    ["#D62728", "#2CA02C", "#FF7F0E", "#9467BD", "#8C564B"],
    ["#CC0000", "#00CC00", "#CCCC00", "#006699", "#CC6600"],
    ["#B22222", "#228B22", "#DAA520", "#4169E1", "#DC143C"],
    ["#FF3333", "#33FF33", "#FF9900", "#3399FF", "#FF33CC"],
    ["#8B0000", "#006400", "#FFD700", "#00008B", "#8B008B"],
    ["#F44336", "#4CAF50", "#FFC107", "#2196F3", "#9C27B0"],
    ["#C0392B", "#27AE60", "#E67E22", "#2980B9", "#8E44AD"],
    ["#E74C3C", "#2ECC71", "#F39C12", "#3498DB", "#1ABC9C"],
    ["#FF6B6B", "#51CF66", "#FFD43B", "#339AF0", "#F06595"],
    ["#D00000", "#007200", "#FFBA08", "#3A86FF", "#8338EC"],
]

# ---------------------------------------------------------------------------
# DEUTERANOPIA-SAFE PALETTES — Blue / Orange high-contrast
# ---------------------------------------------------------------------------
DEUTERANOPIA_PALETTES = [
    ["#0077BB", "#EE7733", "#009988", "#CC3311", "#33BBEE"],
    ["#004488", "#DDAA33", "#BB5566", "#000000", "#AAAA00"],
    ["#1A5276", "#E67E22", "#2E86C1", "#D35400", "#154360"],
    ["#003F88", "#FCA311", "#00509D", "#E63946", "#023E8A"],
    ["#0072B2", "#E69F00", "#56B4E9", "#D55E00", "#009E73"],  # Wong palette
    ["#005F73", "#EE9B00", "#94D2BD", "#CA6702", "#001219"],
    ["#023E8A", "#FB8500", "#0077B6", "#FFB703", "#03045E"],
    ["#1B4F72", "#F39C12", "#2E86C1", "#E67E22", "#154360"],
    ["#0A3D62", "#F8A01E", "#1E90FF", "#FF6B35", "#003D5B"],
    ["#264653", "#E76F51", "#2A9D8F", "#F4A261", "#023047"],
    ["#0066CC", "#FF8800", "#0044AA", "#FF6600", "#003388"],
    ["#003566", "#FFC300", "#001D3D", "#FFD60A", "#000814"],
]

# ---------------------------------------------------------------------------
# PROTANOPIA-SAFE PALETTES — Blue / Yellow / Purple distinctions
# ---------------------------------------------------------------------------
PROTANOPIA_PALETTES = [
    ["#0077BB", "#EECC66", "#EE99AA", "#BBBBBB", "#44BB99"],
    ["#332288", "#DDCC77", "#88CCEE", "#882255", "#117733"],
    ["#0050A0", "#FFD700", "#5DA5DA", "#B276B2", "#60BD68"],
    ["#1B4F72", "#F1C40F", "#154360", "#6C3483", "#1A5276"],
    ["#003049", "#FCBF49", "#D62828", "#F77F00", "#EAE2B7"],
    ["#4059AD", "#F2DC5D", "#6B4226", "#C9D6DF", "#1E3A5F"],
    ["#3A0CA3", "#F8961E", "#560BAD", "#F3722C", "#480CA8"],
    ["#023E8A", "#FFDD00", "#7209B7", "#F72585", "#3A0CA3"],
    ["#0D47A1", "#FFEB3B", "#4A148C", "#CE93D8", "#1565C0"],
    ["#1B2A4A", "#E2B33C", "#3B1F8C", "#C4A1D9", "#0D1B2A"],
    ["#003F88", "#FECB00", "#6A0DAD", "#C9A0DC", "#001F5B"],
    ["#0047AB", "#FFD700", "#5B2C8C", "#D7A8E0", "#001F7A"],
]

# ---------------------------------------------------------------------------
# MONOCHROMACY-SAFE PALETTES — High-contrast grayscale
# ---------------------------------------------------------------------------
MONOCHROMACY_PALETTES = [
    ["#000000", "#404040", "#808080", "#BFBFBF", "#F2F2F2"],
    ["#1A1A1A", "#4D4D4D", "#808080", "#B3B3B3", "#E6E6E6"],
    ["#0D0D0D", "#3D3D3D", "#6E6E6E", "#9E9E9E", "#CFCFCF"],
    ["#111111", "#444444", "#777777", "#AAAAAA", "#DDDDDD"],
    ["#050505", "#2A2A2A", "#555555", "#808080", "#ABABAB"],
    ["#0A0A0A", "#383838", "#666666", "#949494", "#C2C2C2"],
    ["#181818", "#484848", "#787878", "#A8A8A8", "#D8D8D8"],
    ["#0F0F0F", "#3C3C3C", "#6A6A6A", "#979797", "#C5C5C5"],
    ["#121212", "#424242", "#727272", "#A2A2A2", "#D2D2D2"],
    ["#080808", "#303030", "#585858", "#808080", "#A8A8A8"],
    ["#1F1F1F", "#4F4F4F", "#7F7F7F", "#AFAFAF", "#DFDFDF"],
    ["#000000", "#333333", "#666666", "#999999", "#CCCCCC"],
]

# Hatch patterns — each section gets a unique texture for monochromacy
HATCH_PATTERNS = ["", "///", "xxx", "...", "+++", "\\\\", "ooo", "***", "--", "||"]


def get_palette(mode: str) -> list:
    """Return a random safe palette for the given colorblind mode."""
    if mode == "deuteranopia":
        return random.choice(DEUTERANOPIA_PALETTES)
    elif mode == "protanopia":
        return random.choice(PROTANOPIA_PALETTES)
    elif mode == "monochromacy":
        return random.choice(MONOCHROMACY_PALETTES)
    raise ValueError(f"Unknown mode: {mode}")


def get_standard_palette() -> list:
    return random.choice(STANDARD_PALETTES)


def get_hatches() -> list:
    """Return a shuffled list of distinct hatch patterns."""
    h = HATCH_PATTERNS[:]
    random.shuffle(h)
    return h


# ---------------------------------------------------------------------------
# SWATCH GENERATOR — builds start_2 "paint chip card" image
# ---------------------------------------------------------------------------
def draw_swatch(colors: list, mode: str, path: Path):
    """
    Generates a palette key image (start_2): a vertical stack of solid color
    stripes — no text, no data, no shapes. Pure color information only.
    The LoRA learns: "these are the colors to apply to the chart."
    """
    n = len(colors)
    fig, ax = plt.subplots(figsize=(FIG_INCHES, FIG_INCHES))
    fig.patch.set_facecolor("#1A1A1A")   # Neutral dark surround
    ax.set_facecolor("#1A1A1A")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n)
    ax.axis("off")

    stripe_height = 0.82          # relative height of each color bar
    gap           = (1.0 - stripe_height) / 2   # top/bottom padding per stripe

    for i, hex_color in enumerate(colors):
        y_bottom = i + gap
        rect = plt.Rectangle(
            (0.08, y_bottom),   # slight horizontal margin
            0.84,               # width
            stripe_height,
            facecolor=hex_color,
            edgecolor="none",
            linewidth=0,
        )
        ax.add_patch(rect)

    fig.savefig(
        str(path), dpi=DPI,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        format="jpeg",
        pil_kwargs={"quality": JPG_QUALITY, "optimize": True},
    )
    plt.close(fig)
