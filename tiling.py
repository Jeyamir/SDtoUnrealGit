import sys
from PIL import Image, ImageDraw
import numpy as np
from PIL import Image, ImageDraw

def square_mask(img):
    """Roll the images 50% vertical and horz and mask the new center for in-fill"""
    w, h = img.size
    x = np.roll(np.roll(np.array(img), h // 2, 0), w // 2, 1)

    img2 = Image.fromarray(x)
    mask = Image.fromarray(np.zeros_like(x)[:, :, 0])

    draw = ImageDraw.Draw(mask)
    coords = [(w / 2, 0), (w, h / 2), (w / 2, h), (0, h / 2)]
    draw.polygon(coords, fill=255)

    return img2, mask

image = Image.open("/home/albert/seamlesstexturegen/00007-440204137.png")
output_img, output_msk = square_mask(image)
output_img.save("/home/albert/seamlesstexturegen/rolledimage.jpg")