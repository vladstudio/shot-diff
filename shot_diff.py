#!/usr/bin/env python3
"""
Smart Screenshot Comparison Utility

Compares two same-width images, generates pixel-difference maps, clusters differences
into bounding rectangles, and outputs transparent overlays.
"""

import argparse
import json
import numpy as np
from PIL import Image, ImageDraw
import cv2
from pathlib import Path
from typing import Tuple, List


class ShotDiff:
    def __init__(self, diff_threshold: int = 80, min_area: int = 100, padding: int = 5):
        """
        Initialize the ShotDiff utility.
        
        Args:
            diff_threshold: Pixel difference threshold (0-255)
            min_area: Minimum rectangle area to keep (ignore noise)  
            padding: Expand rectangles by this many pixels
        """
        self.diff_threshold = diff_threshold
        self.min_area = min_area
        self.padding = padding
    
    def load_images(self, img1_path: str, img2_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load and preprocess two images for comparison."""
        img1 = Image.open(img1_path).convert('RGB')
        img2 = Image.open(img2_path).convert('RGB')
        
        # Ensure same dimensions
        if img1.size != img2.size:
            raise ValueError(f"Images must have same dimensions. Got {img1.size} and {img2.size}")
        
        return np.array(img1), np.array(img2)
    
    def generate_diff_map(self, img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        """Generate grayscale difference map between two images."""
        # Calculate per-pixel RGB differences
        diff = np.abs(img1.astype(int) - img2.astype(int))
        
        # Convert to grayscale using L2 norm
        diff_gray = np.sqrt(np.sum(diff ** 2, axis=2))
        
        # Normalize to 0-255
        diff_normalized = (diff_gray / diff_gray.max() * 255).astype(np.uint8)
        
        return diff_normalized
    
    def threshold_differences(self, diff_map: np.ndarray) -> np.ndarray:
        """Apply threshold to create binary mask of significant differences."""
        mask = (diff_map > self.diff_threshold).astype(np.uint8) * 255
        return mask
    
    def detect_contours(self, mask: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect contours and extract bounding rectangles."""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangles = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter out small areas
            if w * h >= self.min_area:
                # Apply padding
                x = max(0, x - self.padding)
                y = max(0, y - self.padding)
                w = min(mask.shape[1] - x, w + 2 * self.padding)
                h = min(mask.shape[0] - y, h + 2 * self.padding)
                
                rectangles.append((x, y, w, h))
        
        return rectangles
    
    def create_overlay(self, img_shape: Tuple[int, int], rectangles: List[Tuple[int, int, int, int]]) -> Image.Image:
        """Create transparent overlay with bounding rectangles."""
        # Create transparent RGBA image
        overlay = Image.new('RGBA', (img_shape[1], img_shape[0]), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Draw semi-transparent red rectangles
        for x, y, w, h in rectangles:
            # Rectangle outline
            draw.rectangle([x, y, x + w, y + h], outline=(255, 0, 0, 255), width=2)
            # Semi-transparent fill
            draw.rectangle([x, y, x + w, y + h], fill=(255, 0, 0, 64))
        
        return overlay
    
    def compare_images(self, img1_path: str, img2_path: str, output_dir: str = "output"):
        """
        Complete image comparison workflow.
        
        Returns:
            dict: Results containing paths and rectangle count
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate output filename prefix from input filenames
        img1_name = Path(img1_path).stem
        img2_name = Path(img2_path).stem
        prefix = f"{img1_name}_{img2_name}"
        
        # Load images
        img1, img2 = self.load_images(img1_path, img2_path)
        
        # Generate difference map
        diff_map = self.generate_diff_map(img1, img2)
        
        # Threshold differences
        mask = self.threshold_differences(diff_map)
        
        # Detect contours and get bounding rectangles
        rectangles = self.detect_contours(mask)
        
        # Create overlay
        overlay = self.create_overlay(img1.shape, rectangles)
        
        # Save overlay
        overlay_path = output_path / f"{prefix}_rectangles.png"
        overlay.save(overlay_path)
        
        # Save rectangle data as JSON
        json_path = output_path / f"{prefix}_rectangles.json"
        rectangle_data = [{"x": x, "y": y, "w": w, "h": h} for x, y, w, h in rectangles]
        with open(json_path, 'w') as f:
            json.dump(rectangle_data, f, indent=2)
        
        return {
            "overlay_path": str(overlay_path),
            "json_path": str(json_path),
            "rectangles_found": len(rectangles),
            "rectangles": rectangles
        }


def main():
    parser = argparse.ArgumentParser(description="Smart Screenshot Comparison Utility")
    parser.add_argument("img1", help="Path to first image")
    parser.add_argument("img2", help="Path to second image")
    parser.add_argument("-t", "--threshold", type=int, default=80, 
                       help="Pixel difference threshold (0-255), default: 80")
    parser.add_argument("-m", "--min-area", type=int, default=100,
                       help="Minimum rectangle area to keep, default: 100")
    parser.add_argument("-p", "--padding", type=int, default=5,
                       help="Rectangle padding in pixels, default: 5")
    parser.add_argument("-o", "--output", default="output",
                       help="Output directory, default: output")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Create ShotDiff instance
    shot_diff = ShotDiff(
        diff_threshold=args.threshold,
        min_area=args.min_area,
        padding=args.padding
    )
    
    try:
        # Run comparison
        results = shot_diff.compare_images(args.img1, args.img2, args.output)
        
        print(f"Comparison complete!")
        print(f"Rectangle overlay saved to: {results['overlay_path']}")
        print(f"Rectangle data saved to: {results['json_path']}")
        print(f"Found {results['rectangles_found']} difference regions")
        
        if args.verbose and results['rectangles']:
            print("\nRectangle details:")
            for i, (x, y, w, h) in enumerate(results['rectangles']):
                print(f"  {i+1}: x={x}, y={y}, width={w}, height={h}, area={w*h}")
                
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())