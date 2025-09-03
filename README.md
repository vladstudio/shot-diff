# Shot Diff - Smart Screenshot Comparison Utility

A server-side utility that compares two same-width images, generates pixel-difference maps, clusters differences into bounding rectangles, and outputs transparent overlays.

## Features

- **Pixel-level comparison** with configurable threshold
- **Difference clustering** using contour detection  
- **Noise filtering** by minimum area
- **Visual output** with transparent overlay rectangles
- **CLI interface** with customizable parameters

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python shot_diff.py image1.png image2.png
```

### Advanced Usage
```bash
python shot_diff.py image1.png image2.png \
  --threshold 50 \
  --min-area 200 \
  --padding 10 \
  --output results \
  --verbose
```

### Parameters

- `--threshold, -t`: Pixel difference threshold (0-255), default: 30
- `--min-area, -m`: Minimum rectangle area to keep, default: 100  
- `--padding, -p`: Rectangle padding in pixels, default: 5
- `--output, -o`: Output directory, default: output
- `--verbose, -v`: Show detailed rectangle information

## Output Files

- `diff_map.png`: Grayscale difference map (debugging)
- `rectangles.png`: Transparent overlay with bounding rectangles

## Example

```bash
python shot_diff.py screenshot1.png screenshot2.png --verbose
```

Output:
```
Comparison complete!
Difference map saved to: output/diff_map.png
Rectangle overlay saved to: output/rectangles.png  
Found 3 difference regions

Rectangle details:
  1: x=150, y=200, width=120, height=80, area=9600
  2: x=400, y=100, width=200, height=50, area=10000
  3: x=50, y=500, width=300, height=150, area=45000
```