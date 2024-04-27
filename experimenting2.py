import cv2
import numpy as np

# Load your image (make sure the path and image file are correct)
image = cv2.imread("D:\\Projects\\SDtoUnreal\\depth_map.png", cv2.IMREAD_GRAYSCALE)

# Check if the image needs to be inverted (assuming black areas are to be dilated)
# If your black areas are actually white in the image, you would invert the image colors.
# image = cv2.bitwise_not(image)

# Invert the image so black becomes white and white becomes black
inverted_image = cv2.bitwise_not(image)


cv2.imwrite('output_inverted.jpg', inverted_image)

# Define the dilation kernel size
kernel_size = 5
kernel = np.ones((kernel_size, kernel_size), np.uint8)

# Dilate the image, which expands the white areas in this case
dilated_image = cv2.dilate(inverted_image, kernel, iterations=1)

dilated_image = cv2.erode(dilated_image, kernel, iterations=1)

# If you inverted the image before, invert it back
dilated_image = cv2.bitwise_not(dilated_image)

# Save or display the new image
cv2.imwrite('output_with_expanded_black_areas.jpg', dilated_image)
