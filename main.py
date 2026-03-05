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

import zipfile
import math
from config import PAIRS_PER_MODE, OUTPUT_DIR
from generator import generate_pair

MODES = ["deuteranopia", "protanopia", "monochromacy"]
SETS_PER_ZIP = 300

def main():
    total = PAIRS_PER_MODE * len(MODES)
    total_zips = math.ceil(total / SETS_PER_ZIP)

    print("=" * 64)
    print("  Colorblind-Safe Data Palette Swapper")
    print("  LoRA Multi-Image Edit Dataset Generator  v2.0")
    print("=" * 64)
    print(f"  Output  : {OUTPUT_DIR.resolve()}")
    print(f"  Per mode: {PAIRS_PER_MODE}  |  Total pairs: {total}")
    print(f"  Files   : Zipped in chunks of max {SETS_PER_ZIP} sets ({total_zips} archive(s))")
    print("-" * 64)

    pair_index = 1
    zip_file_count = 1
    sets_in_zip = 0
    current_zip = None
    total_generated = 0

    for mode in MODES:
        print(f"\n[{mode.upper()}]")
        for _ in range(PAIRS_PER_MODE):
            if current_zip is None:
                zip_path = OUTPUT_DIR / f"dataset_{zip_file_count:03d}.zip"
                current_zip = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)

            chart_title = generate_pair(pair_index, mode)
            
            # Add exactly the 4 generated files to the zip archive
            files_to_zip = [
                f"{pair_index}_start_1.jpg",
                f"{pair_index}_start_2.jpg",
                f"{pair_index}_end.jpg",
                f"{pair_index}.txt"
            ]
            
            for f in files_to_zip:
                file_path = OUTPUT_DIR / f
                current_zip.write(file_path, arcname=f)
                file_path.unlink()  # Delete the loose file
                
            print(f"  ✓ {pair_index:03d}  [{mode:>12s}]  {chart_title}")
            
            pair_index += 1
            sets_in_zip += 1
            total_generated += 1
            
            if sets_in_zip >= SETS_PER_ZIP:
                current_zip.close()
                current_zip = None
                sets_in_zip = 0
                zip_file_count += 1
                
            if total_generated >= 40:
                break
                
        if total_generated >= 40:
            break

    if current_zip is not None:
        current_zip.close()

    print("\n" + "=" * 64)
    print(f"  Done — {total_generated} pairs packed into {zip_file_count if sets_in_zip > 0 else zip_file_count - 1} ZIP archive(s).")
    print(f"  {OUTPUT_DIR.resolve()}")
    print("=" * 64)


if __name__ == "__main__":
    main()