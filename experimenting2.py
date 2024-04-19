import cv2
import numpy as np

def local_contrast_normalization(image, block_size=21, clip_limit=2.0):
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to each block
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(block_size, block_size))
    equalized_image = clahe.apply(image)
    
    # Convert the equalized image to float32 for further processing
    equalized_image_float = np.float32(image) / 255.0
    
    # Calculate the local mean and standard deviation using a square window
    local_mean = cv2.boxFilter(equalized_image_float, -1, (block_size, block_size))
    local_mean_squared = cv2.boxFilter(equalized_image_float**2, -1, (block_size, block_size))
    local_std_dev = np.sqrt(local_mean_squared - local_mean**2)
    
    # Normalize each pixel based on local mean and standard deviation
    normalized_image = (equalized_image_float - local_mean) / (local_std_dev + 1e-5)
    
    # Clip the values to [0, 1] range and convert back to uint8
    normalized_image = np.uint8(np.clip(normalized_image * 255.0, 0, 255))
    
    return normalized_image

# Load grayscale image
image = cv2.imread("D:\\Projects\\SDtoUnreal\\depth_map.png", cv2.IMREAD_GRAYSCALE)

# Apply local contrast normalization
normalized_image = local_contrast_normalization(image)

# Save the normalized image
cv2.imwrite('normalized_image.jpg', normalized_image)