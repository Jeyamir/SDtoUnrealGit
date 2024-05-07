import cv2
import numpy as np

def calculate_normal_map(height_map_filename):
    # Load the height map as a grayscale image
    height_map = cv2.imread(height_map_filename, cv2.IMREAD_GRAYSCALE)
    
    # Compute gradients in the x and y directions
    sobel_x = cv2.Sobel(height_map, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(height_map, cv2.CV_64F, 0, 1, ksize=3)
    
    # Calculate the z component of the normal (assuming depth is 1 for all normals)
    z = np.ones_like(sobel_x)
    
    # Normalize the gradients to create normal vectors
    normal_map = np.dstack((sobel_x, sobel_y, z))
    norms = np.linalg.norm(normal_map, axis=2)
    normal_map_normalized = normal_map / norms[:,:,None]
    
    # Map components from [-1, 1] to [0, 255]
    normal_map_normalized = ((normal_map_normalized + 1) / 2 * 255).astype(np.uint8)
    
    return normal_map_normalized

# Usage example:
normal_map = calculate_normal_map("D:\\Projects\\SDtoUnreal\\flat rock wall depth_map.png")
cv2.imwrite('normal_map_output.png', normal_map)  # Save the image instead of showing it
