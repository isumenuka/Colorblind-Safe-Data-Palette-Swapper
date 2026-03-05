"""
captions.py — English-language caption templates for LoRA training prompts.

These prompts instruct the model to use start_2 as a color reference and apply it to start_1.
"""
import random

# ---------------------------------------------------------------------------
# DEUTERANOPIA — Blue / Orange high-contrast replacement
# ---------------------------------------------------------------------------
DEUTERANOPIA_CAPTIONS = [
    "Replace the chart colors in Image 1 with the color palette in Image 2, keeping all text, data, and geometric structures absolutely unchanged.",
    "Recolor the chart in Image 1 using the blue and orange palette from Image 2. Do not alter any axes, labels, or data values.",
    "Apply the high-contrast deuteranopia-safe palette from Image 2 to the data visualization in Image 1, preserving identical chart geometry.",
    "Transform the red and green areas of the chart in Image 1 into the blue and orange tones shown in Image 2, maintaining exact structural consistency.",
    "Use the color swatch in Image 2 as a reference to replace the inaccessible colors in Image 1. All text and shapes must remain unchanged.",
    "Map the colors of the chart in Image 1 to the deuteranopia-friendly palette provided in Image 2 without modifying any geometric elements.",
    "Convert the color scheme of Image 1 to the accessible blue-orange palette in Image 2. All data points, legends, and labels must stay exactly the same.",
    "Following the color key in Image 2, replace the colors in the data visualization in Image 1 while keeping the layout and typography absolutely intact.",
    "Replace the confusing red-green hues in Image 1 with the clear blue and orange palette from Image 2, preserving the chart's structure perfectly.",
    "Apply a deuteranopia color correction to Image 1 using the reference colors in Image 2. Do not change any text, data, or geometric structures.",
]

# ---------------------------------------------------------------------------
# PROTANOPIA — Blue / Yellow high-contrast replacement
# ---------------------------------------------------------------------------
PROTANOPIA_CAPTIONS = [
    "Replace the chart colors in Image 1 with the blue and yellow color palette in Image 2, keeping all text, data, and geometric structures absolutely unchanged.",
    "Recolor the chart in Image 1 using the protanopia-safe palette from Image 2. Do not alter any axes, legends, or data values.",
    "Apply the high-contrast blue and yellow palette from Image 2 to the data visualization in Image 1, preserving the exact same chart geometry.",
    "Transform the inaccessible colors of the chart in Image 1 into the distinct blue and yellow tones shown in Image 2, maintaining structural consistency.",
    "Use the color swatch in Image 2 to replace the colors in Image 1, making it protanopia-friendly. All text and shapes must remain strictly unchanged.",
    "Map the colors of the chart in Image 1 to the accessible palette provided in Image 2 without modifying any geometric or text elements.",
    "Convert the color scheme of Image 1 to the safe blue-yellow palette in Image 2. All data points and labels must remain exactly as they are.",
    "Following the color key in Image 2, replace the colors in the data visualization in Image 1 while keeping the layout absolutely intact.",
    "Replace the hues causing protanopia confusion in Image 1 with the clear palette from Image 2, preserving the chart's structure perfectly.",
    "Apply a protanopia color correction to Image 1 using the reference colors in Image 2. Do not alter any text, data, or geometric structures.",
]

# ---------------------------------------------------------------------------
# MONOCHROMACY — Grayscale + hatch patterns
# ---------------------------------------------------------------------------
MONOCHROMACY_CAPTIONS = [
    "Replace the chart colors in Image 1 with the grayscale palette in Image 2, and add distinct texture fills to each data area, keeping all text and geometry unchanged.",
    "Convert the chart in Image 1 to a monochromacy-safe version using the high-contrast grayscale palette from Image 2. Add unique patterns to each section.",
    "Apply the grayscale palette from Image 2 to the data visualization in Image 1, adding hatching patterns (lines, dots, crosses) while preserving chart geometry.",
    "Transform the colored chart in Image 1 into a grayscale version based on Image 2, applying distinct textures to each category for accessibility.",
    "Use the grayscale color swatch in Image 2 as a reference to recolor Image 1. Add different patterns to each data series without modifying any text or shapes.",
    "Map the colors of the chart in Image 1 to the grayscale palette provided in Image 2, adding distinguishable textures to all elements without modifying chart geometry.",
    "Convert the color scheme of Image 1 to the highly separated grayscale palette in Image 2, and overlay unique texture fills on each segment.",
    "Following the grayscale key in Image 2, replace the colors in Image 1 and apply distinct pattern fills, while keeping the layout and typography absolutely intact.",
    "Replace the colors in Image 1 with the grayscale tones from Image 2 and add textures like stripes or dots to each area. Preserve the chart's structure perfectly.",
    "Apply an achromatopsia color correction to Image 1 using the grayscale reference in Image 2. Add texture fills to each section. Do not change any text or data.",
]


def get_caption(mode: str) -> str:
    if mode == "deuteranopia":
        return random.choice(DEUTERANOPIA_CAPTIONS)
    elif mode == "protanopia":
        return random.choice(PROTANOPIA_CAPTIONS)
    elif mode == "monochromacy":
        return random.choice(MONOCHROMACY_CAPTIONS)
    raise ValueError(f"Unknown mode: {mode}")
