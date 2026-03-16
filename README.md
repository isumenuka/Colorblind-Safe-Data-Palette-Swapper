# Colorblind-Safe Data Palette Swapper

**LoRA Multi-Image Edit Dataset Generator v2.0**

A specialized tool for generating high-quality datasets designed to train image-to-image models (such as LoRA/ControlNet) to transform inaccessible, color-heavy data visualizations into colorblind-safe formats.

## 🚀 Overview

This project automates the creation of a "color-swap" dataset. It generates pairs of charts where the geometry is identical but the color palette is transformed from an "inaccessible" standard palette to a "safe" palette (Deuteranopia, Protanopia, or Monochromacy).

### Key Features
- **LoRA-Focused Training**: Outputs multi-image sets (`start_1`, `start_2`, `end`) that teach models the relationship between source charts and target palettes.
- **Seeded Geometry**: Uses independent random number generators for data and styling, ensuring that "before" and "after" images are pixel-perfect in geometry.
- **WCAG Contrast Awareness**: Automatically selects optimal text colors (black/white) for labels based on background luminance.
- **High Resolution**: Default output is 1024×1024, matching modern image model base sizes.

## 📊 Supported Charts & Modes

### Colorblind Modes
1. **Deuteranopia**: Blue/Orange high-contrast palettes.
2. **Protanopia**: Blue/Yellow/Purple distinction-focused palettes.
3. **Monochromacy**: High-contrast grayscale with distinct hatch patterns for tactile-like differentiation.

### Chart Types
- Pie Charts
- Bar Charts (Grouped)
- Stacked Bar Charts
- Line Charts (with markers)
- Area Charts (Stacked)
- Scatter Plots
- Heatmaps

## 📁 Dataset Structure

The generator packs data into ZIP archives (max 300 sets per archive). Each training set consists of:

| File | Type | Description |
| :--- | :--- | :--- |
| `N_start_1.jpg` | **Source Chart** | The original chart with inaccessible "standard" colors. |
| `N_start_2.jpg` | **Palette Key** | A vertical "paint chip" image showing the target safe palette colors. |
| `N_end.jpg` | **Target Chart** | The transformed chart using the safe palette (and hatches for Monochromacy). |
| `N.txt` | **Caption** | Training prompt including mode and chart description. |

## 🛠️ Usage

### Installation
Ensure you have Python 3.x and the required dependencies installed:
```bash
pip install matplotlib numpy
```

### Running the Generator
Simply execute the main orchestration script:
```bash
python main.py
```
Outputs will be saved in the `dataset_output` directory.

## ⚙️ Configuration

Modify `config.py` to adjust:
- `IMG_SIZE`: Output resolution (default: 1024).
- `PAIRS_PER_MODE`: Number of sets to generate per colorblind mode.
- `OUTPUT_DIR`: Path to save the resulting ZIP archives.

## 📄 File Layout
- `config.py`: Global constants (resolution, DPI, counts).
- `palettes.py`: Palette definitions and palette-key image generator.
- `charts.py`: Flat-style chart drawing functions (seeded for geometry persistence).
- `generator.py`: Logic for generating the 4-file sets.
- `captions.py`: LoRA training captions (supports Chinese-language prompts).
- `main.py`: Main orchestration and ZIP packing logic.
