"""
main.py — Entry point for the Colorblind-Safe Data Palette Swapper.

Run:  python main.py

File layout:
    config.py    — resolution, DPI, output dir, pair count
    palettes.py  — palette lists + palette swatch (start_2) generator
    charts.py    — flat chart drawing functions (pie, bar, stacked bar,
                   line, area, scatter, heatmap)
    captions.py  — Chinese-language LoRA training captions
    generator.py — seeded pair generation (ensures start_1 ≡ end in geometry)
    main.py      — this file: orchestration only
"""

from config import PAIRS_PER_MODE, OUTPUT_DIR
from generator import generate_pair

MODES = ["deuteranopia", "protanopia", "monochromacy"]


def main():
    total = PAIRS_PER_MODE * len(MODES)

    print("=" * 64)
    print("  Colorblind-Safe Data Palette Swapper")
    print("  LoRA Multi-Image Edit Dataset Generator  v2.0")
    print("=" * 64)
    print(f"  Output  : {OUTPUT_DIR.resolve()}")
    print(f"  Per mode: {PAIRS_PER_MODE}  |  Total pairs: {total}")
    print(f"  Files   : {total * 4}  (×_start_1, ×_start_2, ×_end, ×.txt)")
    print("-" * 64)

    pair_index = 1
    for mode in MODES:
        print(f"\n[{mode.upper()}]")
        for _ in range(PAIRS_PER_MODE):
            chart_title = generate_pair(pair_index, mode)
            print(f"  ✓ {pair_index:03d}  [{mode:>12s}]  {chart_title}")
            pair_index += 1

    print("\n" + "=" * 64)
    print(f"  Done — {total} pairs, {total * 4} files.")
    print(f"  {OUTPUT_DIR.resolve()}")
    print("=" * 64)


if __name__ == "__main__":
    main()