import cv2
import os
import numpy as np
from typing import Tuple, Dict, Any

from screencap import make_dir_relative

DIVISIONS = (25, 25)

def _calculate_cell_dimensions(img_shape: Tuple[int, ...], 
                               divisions: Tuple[int, int]) -> Tuple[int, int]:
    """
    Calculates the pixel height and width of a single grid cell.

    Args:
        img_shape: The .shape tuple from the source image.
        divisions: (rows, columns) tuple for grid dimensions.

    Returns:
        A (cell_height, cell_width) tuple in pixels.
    """
    cell_height = img_shape[0] // divisions[0]
    cell_width = img_shape[1] // divisions[1]
    return cell_height, cell_width

def _get_font_properties(font_color: Tuple[int, int, int], font_scale: float, 
                         font_thickness: int) -> Dict[str, Any]:
    """
    Packages font properties into a dictionary for easy passing.

    Args:
        font_color: (B, G, R) color tuple for the text.
        font_scale: The scale factor for the font size.
        font_thickness: The thickness of the font lines in pixels.

    Returns:
        A dictionary containing font properties and padding.
    """
    return {
        "font_face": cv2.FONT_HERSHEY_SIMPLEX,
        "scale": font_scale,
        "color": font_color,
        "thickness": font_thickness,
        "padding_x": 5,
        "padding_y": 25 # Increased padding for larger font
    }

def _get_box_properties(box_color: Tuple[int, int, int], 
                        box_alpha: float) -> Dict[str, Any]:
    """
    Packages box properties into a dictionary.

    Args:
        box_color: (B, G, R) color tuple for the background box.
        box_alpha: The opacity of the background box (0.0 to 1.0).

    Returns:
        A dictionary containing box properties.
    """
    return {
        "color": box_color,
        "alpha": box_alpha
    }

def _draw_label_background_box(img: np.ndarray, text_coords: Tuple[int, int],
                               text_size: Tuple[int, int], baseline: int,
                               box_props: Dict[str, Any], 
                               padding: int) -> np.ndarray:
    """
    Draws a semi-transparent background box for a text label.

    Args:
        img: The source image as a NumPy array.
        text_coords: (x, y) position for the text.
        text_size: (width, height) of the text.
        baseline: The text baseline offset from cv2.getTextSize.
        box_props: Dictionary with box color and alpha.
        padding: Padding to apply around the text.

    Returns:
        The image with the background box blended in.
    """
    text_x, text_y = text_coords
    w, h = text_size
    
    box_x1 = text_x - padding // 2
    box_y1 = text_y - h - padding
    box_x2 = text_x + w + padding // 2
    box_y2 = text_y + baseline - padding // 2
    
    overlay = img.copy()
    cv2.rectangle(overlay, (box_x1, box_y1), (box_x2, box_y2), 
                  box_props["color"], -1)
    return cv2.addWeighted(overlay, box_props["alpha"], img, 1 - box_props["alpha"], 0)

def _draw_label_in_cell(img: np.ndarray, label: int, row: int, col: int, 
                        cell_dims: Tuple[int, int], 
                        font_props: Dict[str, Any], 
                        box_props: Dict[str, Any]) -> np.ndarray:
    """
    Draws a single text label with a background box in its cell.

    Args:
        img: The source image (will be modified).
        label: The number to draw (e.g., 1, 2, 3...).
        row: The current grid row (0-indexed).
        col: The current grid column (0-indexed).
        cell_dims: (cell_height, cell_width) tuple in pixels.
        font_props: A dictionary from _get_font_properties.
        box_props: A dictionary from _get_box_properties.

    Returns:
        The modified image with the label drawn on it.
    """
    cell_height, cell_width = cell_dims
    cell_top = row * cell_height
    cell_left = col * cell_width
    
    text = str(label)
    text_x = cell_left + font_props["padding_x"]
    text_y = cell_top + font_props["padding_y"]
    
    (w, h), baseline = cv2.getTextSize(text, font_props["font_face"], 
                                      font_props["scale"], font_props["thickness"])

    img = _draw_label_background_box(
        img, (text_x, text_y), (w,h), baseline, 
        box_props, font_props["padding_x"]
    )

    cv2.putText(
        img, text, (text_x, text_y),
        font_props["font_face"], font_props["scale"], font_props["color"],
        font_props["thickness"], cv2.LINE_AA
    )
    return img

def add_labels(img: np.ndarray, divisions: Tuple[int, int], 
               font_color: Tuple[int, int, int], font_scale: float, 
               font_thickness: int, box_color: Tuple[int, int, int], 
               box_alpha: float) -> np.ndarray:
    """
    Orchestrates adding sequentially numbered labels to each cell of a grid.

    Args:
        img: The source image as a NumPy array.
        divisions: (rows, columns) tuple for grid dimensions.
        font_color: (B, G, R) color tuple for the text.
        font_scale: The scale factor for the font size.
        font_thickness: The thickness of the font lines in pixels.
        box_color: (B, G, R) color tuple for the background box.
        box_alpha: The opacity of the background box (0.0 to 1.0).

    Returns:
        The image with all labels added.
    """
    print(f"INFO: Adding {divisions[0] * divisions[1]} labels to image")
    
    cell_dims = _calculate_cell_dimensions(img.shape, divisions)
    font_props = _get_font_properties(font_color, font_scale, font_thickness)
    box_props = _get_box_properties(box_color, box_alpha)
    
    label_number = 1
    for r in range(divisions[0]):
        for c in range(divisions[1]):
            img = _draw_label_in_cell(
                img, label_number, r, c, 
                cell_dims, font_props, box_props
            )
            label_number += 1
            
    return img


def get_labeled_screenshot(source: str) -> str:
    source_name = source.split('/')[-1]
    output_name = f"labeled_{source_name}"
    
    img = cv2.imread(source)

    divisions = DIVISIONS         # 20 rows, 20 columns
    
    text_color = (255, 255, 255) # White (BGR)
    font_scale = 0.6             # Increased from 0.6
    font_thickness = 1
    
    box_color = (0, 0, 0)        # Black (BGR)
    box_alpha = 0.4              # 70% opaque
    
    # 1. Add numbered labels
    output = add_labels(
        img, 
        divisions, 
        font_color=text_color, 
        font_scale=font_scale, 
        font_thickness=font_thickness,
        box_color=box_color,
        box_alpha=box_alpha
    )

    FOLDER = "labeled_screencaps"
    folder_path = make_dir_relative(FOLDER)
    labeled_screenshot_path = os.path.join(folder_path, output_name)

    cv2.imwrite(labeled_screenshot_path, output)
    print(f"INFO: Successfully saved labeled image to {output_name}")

    return labeled_screenshot_path


if __name__ == '__main__':
    get_labeled_screenshot("screencaps/2025-11-07_01-49-20.png")