"""
generator.py — Core dataset pair generation logic.

For every pair (N), generates exactly 4 files:
  N_start_1.jpg — Inaccessible chart drawn with a standard red/green palette
  N_start_2.jpg — Palette swatch / paint-chip card (colors only, no data)
  N_end.jpg     — The SAME chart redrawn with the colorblind-safe palette
  N.txt         — Chinese-language training caption

CRITICAL: start_1 and end share the SAME random seed so every axis tick,
every wedge size, every data point, every label is bit-for-bit identical.
Only the colors differ — the LoRA learns ONLY a color mapping rule.
"""

import random as _random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from config import OUTPUT_DIR, IMG_SIZE, DPI, FIG_INCHES, JPG_QUALITY
from palettes import (
    get_standard_palette, get_palette, get_hatches,
    draw_swatch,
)
from charts import CHART_DRAWERS, _title as _make_title, _labels
from captions import get_caption


# ---------------------------------------------------------------------------
# FIGURE / SAVE HELPERS
# ---------------------------------------------------------------------------

def _new_fig():
    """Create a new 1024×1024 figure."""
    fig, ax = plt.subplots(figsize=(FIG_INCHES, FIG_INCHES))
    return fig, ax


def _save(fig: plt.Figure, path: Path):
    """Save figure as 1024×1024 JPEG and close it."""
    fig.savefig(
        str(path),
        dpi=DPI,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        format="jpeg",
        pil_kwargs={"quality": JPG_QUALITY, "optimize": True},
    )
    plt.close(fig)


# ---------------------------------------------------------------------------
# PAIR GENERATOR
# ---------------------------------------------------------------------------

def generate_pair(pair_index: int, mode: str) -> str:
    """
    Generate one complete Multi-Image Edit Dataset pair.

    Returns the chart title string for console logging.
    """
    # --- Choose chart type & title (outer seed so these are stable) ---
    outer_py  = _random.Random(pair_index * 997)
    drawer    = outer_py.choice(CHART_DRAWERS)
    title     = _make_title(outer_py)

    # --- Choose palettes ---
    std_palette  = get_standard_palette()   # inaccessible red/green palette
    safe_palette = get_palette(mode)         # colorblind-safe target palette
    hatches      = get_hatches() if mode == "monochromacy" else None

    # -----------------------------------------------------------------------
    # start_1 — inaccessible chart
    # Uses a seeded RNG so exact same data is reproducible for end.
    # -----------------------------------------------------------------------
    seed = pair_index * 31337   # deterministic per pair

    rng_np  = np.random.default_rng(seed)
    rng_py  = _random.Random(seed)

    fig1, ax1 = _new_fig()
    drawer(ax1, fig1, std_palette, hatches=None, rng=rng_np, rng_py=rng_py, title=title)
    _save(fig1, OUTPUT_DIR / f"{pair_index}_start_1.jpg")

    # -----------------------------------------------------------------------
    # start_2 — palette swatch (paint-chip card, NO chart data)
    # Shows the colorblind-safe colors the model must apply.
    # -----------------------------------------------------------------------
    draw_swatch(safe_palette, mode, OUTPUT_DIR / f"{pair_index}_start_2.jpg")

    # -----------------------------------------------------------------------
    # end — SAME chart redrawn with safe palette, IDENTICAL seed → same data
    # -----------------------------------------------------------------------
    rng_np2 = np.random.default_rng(seed)   # reset to same seed
    rng_py2 = _random.Random(seed)           # reset to same seed

    fig3, ax3 = _new_fig()
    drawer(ax3, fig3, safe_palette, hatches=hatches, rng=rng_np2, rng_py=rng_py2, title=title)
    _save(fig3, OUTPUT_DIR / f"{pair_index}_end.jpg")

    # -----------------------------------------------------------------------
    # caption (.txt) — Chinese instruction prompt
    # -----------------------------------------------------------------------
    caption = get_caption(mode)
    (OUTPUT_DIR / f"{pair_index}.txt").write_text(caption, encoding="utf-8")

    return title
