

from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QImage
import numpy as np
import cv2
from scipy.ndimage import convolve

def load_image(file_path, is_uint16=False):
    """Load an image from the file path."""
    image = QImage(file_path)
    if is_uint16:
        # Convert from uint16 to uint8
        image = QImage(image.constBits(), image.width(), image.height(), QImage.Format_Grayscale16)
        image = image.convertToFormat(QImage.Format_Grayscale8)
    return image



def save_image(image, parent=None):
    """Save an image using a file dialog."""
    file_path, _ = QFileDialog.getSaveFileName(parent, "Save Image", ".", "Images (*.png *.jpg *.bmp)")
    if file_path:
        image.save(file_path)

def calculate_occlusion(height_map, radius=5, local_weight=0.5, global_weight=0.5, invert=False):
    """Calculate ambient occlusion with weighted local and global comparisons."""
    # Calculate the global average height
    global_average = np.mean(height_map)
    
    # Define a kernel for local neighborhood averaging
    kernel_size = 2 * radius + 1
    y, x = np.ogrid[-radius:radius+1, -radius:radius+1]
    kernel = (x**2 + y**2 <= radius**2).astype(float)
    kernel[kernel == 1] = 1 / kernel.sum()  # Normalize the kernel to sum to 1

    # Convolve the height map with this kernel for local averages
    local_averages = convolve(height_map.astype(float), kernel, mode='constant', cval=0)
    
    # Calculate occlusion by comparing local and global averages
    local_occlusion = np.where(height_map < local_averages, local_averages - height_map, 0)
    global_occlusion = np.where(height_map < global_average, global_average - height_map, 0)
    
    # Apply weights to each occlusion component
    combined_occlusion = local_weight * local_occlusion + global_weight * global_occlusion
    
    # Normalize and scale the occlusion map
    max_occlusion = np.max(combined_occlusion)
    if max_occlusion > 0:
        occlusion_map = 255 * (combined_occlusion / max_occlusion)
    else:
        occlusion_map = np.zeros_like(combined_occlusion)

    # Invert the occlusion map
    if invert:
        occlusion_map = 255 - occlusion_map

    occlusion_map = occlusion_map.astype(np.uint8)
    return occlusion_map
