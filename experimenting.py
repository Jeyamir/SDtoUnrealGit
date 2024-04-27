from transformers import AutoImageProcessor, AutoModelForDepthEstimation
import torch
import numpy as np
from PIL import Image
import requests
#load local image
#replace \ with \\ in the path
    
image = Image.open("D:\\Projects\\SDtoUnreal\\texture, bark of a tree, front_0.png")
# "D:\Projects\SDtoUnreal\a golden sunset over a forest _0.png"     
image_processor = AutoImageProcessor.from_pretrained("LiheYoung/depth-anything-small-hf")
model = AutoModelForDepthEstimation.from_pretrained("LiheYoung/depth-anything-small-hf")

# prepare image for the model
inputs = image_processor(images=image, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)
    predicted_depth = outputs.predicted_depth

# interpolate to original size
prediction = torch.nn.functional.interpolate(
    predicted_depth.unsqueeze(1),
    size=image.size[::-1],
    mode="bicubic",
    align_corners=False,
)


# visualize the prediction

output = prediction.squeeze().cpu().numpy()
formatted = (output * 255 / np.max(output)).astype("uint8")
formatted[formatted>255] = 0
depth = Image.fromarray(formatted)
depth.save("depth_map.png")