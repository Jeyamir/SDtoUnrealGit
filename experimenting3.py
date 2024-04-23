import cv2
import numpy as np

def circular_average_filter(image_path, radius):
    # Load the image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Create a circular kernel with the specified radius
    kernel_size = 2 * radius + 1
    kernel = np.zeros((kernel_size, kernel_size), dtype=np.uint8)
    y, x = np.ogrid[-radius:radius+1, -radius:radius+1]
    mask = x**2 + y**2 <= radius**2
    kernel[mask] = 1
    
    # Normalize the kernel so that the sum of all elements equals 1
    kernel = kernel / np.sum(kernel)
    
    # Apply the kernel to the image using filter2D
    averaged_image = cv2.filter2D(img, -1, kernel)

    return averaged_image

# Usage example
image_path = "D:\\Projects\\SDtoUnreal\\normalized_image.jpg" # Replace with the actual path to your image
radius = 5  # Radius for averaging
averaged_image = circular_average_filter(image_path, radius)

# Show and save the result
cv2.imshow('Averaged Image', averaged_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('averaged_output.jpg', averaged_image)
