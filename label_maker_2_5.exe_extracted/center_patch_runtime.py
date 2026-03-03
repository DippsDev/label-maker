
# This patches the ImageDraw.text calls to center-align shipping address text

import sys
import os
from PIL import ImageDraw

# Save original text method
_original_text = ImageDraw.ImageDraw.text

# Label width for UPS labels
LABEL_WIDTH = 661
SHIP_TO_CENTER_X = LABEL_WIDTH // 2

# Track which texts are ship-to related based on Y coordinates
SHIP_TO_Y_RANGE = (135, 240)  # Y coordinates for ship-to section

def centered_text(self, xy, text, fill=None, font=None, anchor=None, *args, **kwargs):
    """Wrapper that centers text in the SHIP TO section"""
    x, y = xy
    
    # Check if this is in the SHIP TO section
    if SHIP_TO_Y_RANGE[0] <= y <= SHIP_TO_Y_RANGE[1] and x == 60:
        # Calculate text width
        if font:
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
        else:
            # Estimate if no font (shouldn't happen)
            text_width = len(text) * 10
        
        # Center the text
        centered_x = (LABEL_WIDTH - text_width) // 2
        xy = (centered_x, y)
        print(f"[CENTER] Centering text at y={y}: '{text}' -> x={centered_x}")
    
    # Call original method
    return _original_text(self, xy, text, fill, font, anchor, *args, **kwargs)

# Apply the patch
ImageDraw.ImageDraw.text = centered_text
print("[*] Applied center-align patch to ImageDraw.text()")
