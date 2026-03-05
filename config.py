"""
config.py — Global configuration constants
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("dataset_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# IMAGE SPEC
# Training resolution matching the Qwen-Image base model native size.
# All images (start_1, start_2, end) are exactly this size.
# ---------------------------------------------------------------------------
IMG_SIZE   = 1024       # pixels — both width and height (square)
DPI        = 96         # screen DPI; matplotlib figsize is set from IMG_SIZE/DPI
FIG_INCHES = IMG_SIZE / DPI   # ~10.67 inches — used for all figure sizes
JPG_QUALITY = 95

# ---------------------------------------------------------------------------
# DATASET SIZE
# Quality over quantity: 30 pairs × 3 modes = 90 pristine training examples.
# ---------------------------------------------------------------------------
PAIRS_PER_MODE = 30
