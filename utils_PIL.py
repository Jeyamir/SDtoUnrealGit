import numpy as np
from PIL import Image

def adjust_contrast(image, min_color, max_color, contrast_factor):
        img_array = np.array(image)

        # Normalize pixel values
        normalized_img = img_array / 255.0

        # Centering around center_point
        centered_img = normalized_img - .5

        # Apply contrast adjustment within the color range
        contrast_adjusted_img = centered_img.copy()
        contrast_adjusted_img[(img_array >= min_color) & (img_array <= max_color)] *= contrast_factor

        # Re-centering
        adjusted_img = contrast_adjusted_img + .5

        # Denormalize pixel values
        adjusted_img = np.clip(adjusted_img * 255, 0, 255).astype(np.uint8)

        return Image.fromarray(adjusted_img)


def scale_pixel_range(image, input_min, input_max, output_min, output_max):
    img_array = image.convert("L")  # Convert to grayscale

    # Scale pixel values within the specified input range to the output range
    scaled_img_array = (img_array - input_min) * ((output_max - output_min) / (input_max - input_min)) + output_min

    # Clip values to ensure they are within the output range
    scaled_img_array = scaled_img_array.clip(output_min, output_max)

    # Convert back to image
    scaled_image = Image.fromarray(scaled_img_array.astype('uint8'))

    return scaled_image

def convert_pixel_range(self, image, input_min, input_max, output_min, output_max):
        # Get the dimensions of the image
        # width, height = image.size
        
        # # Create a new empty image with the same size and mode
        # converted_image = Image.new(image.mode, (width, height))
        
        # # Iterate over each pixel
        # for y in range(height):
        #     for x in range(width):
        #         # Get the pixel value at (x, y)
        #         pixel = image.getpixel((x, y))
                
        #         # Check if the pixel value is within the input range
        #         if input_min <= pixel <= input_max:
        #             # Perform the conversion for pixels in the input range
        #             input_range = input_max - input_min
        #             output_range = output_max - output_min
        #             scaled_pixel = int((pixel - input_min) * (output_range / input_range) + output_min)
        #             # Set the converted pixel value in the new image
        #             converted_image.putpixel((x, y), scaled_pixel)
        #         else:
        #             # For pixels outside the input range, keep the original value
        #             converted_image.putpixel((x, y), pixel)
        
        # return converted_image
        if self.input_min <= pixel_value <= self.input_max:
            centered_pixel_value = pixel_value / 255 - center_point
            adjusted_pixel_value = centered_pixel_value * contrast_factor + center_point
            return int(adjusted_pixel_value * 255)
        else:
            return pixel_value`
