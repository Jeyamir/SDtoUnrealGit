# !pip install opencv-python transformers accelerate
from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel, AutoencoderKL
from diffusers.utils import load_image
import numpy as np
import torch
from random import randint
import cv2
from PIL import Image


class ControlNetPipeline:
    def __init__(self):
        self.load_models()
        self.load_default_settings()

    def load_models(self):
        # Placeholder for model initialization
        controlnet_conditioning_scale = 0.5  # recommended for good generalization
        self.controlnet = ControlNetModel.from_pretrained(
            "diffusers/controlnet-canny-sdxl-1.0", torch_dtype=torch.float16
        )
        self.vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
        self.pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            controlnet=self.controlnet,
            vae=self.vae,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16",
        )
        self.pipe.enable_model_cpu_offload()
        # self.pipe.enable_xformers_memory_efficient_attention()
        

    def generate_image(self, index):
        # Download and prepare the canny image
        image = load_image(
    "https://hf.co/datasets/hf-internal-testing/diffusers-images/resolve/main/sd_controlnet/hf-logo.png"
)
        canny_image = self.gen_canny(image)
        # Image generation
        output_image = self.pipe(
            prompt=self.prompt,
            negative_prompt=self.negative_prompt,
            controlnet_conditioning_scale=0.5,
            image=canny_image
        ).images[0]

        file_path = f"./generated_image_{index}.png"
        output_image.save(file_path)
        return file_path

    def load_default_settings(self):
        # Example settings
        self.set_prompts("aerial view, a futuristic research complex in a bright foggy jungle, hard lighting", 
                         negative_prompt="low quality, bad quality, sketches")
        self.set_inference_steps(30)
        self.set_CFG(5.0)
        self.set_height(512)
        self.set_width(512)
        self.set_seed(randint(1, 999999))

    # Placeholder methods for settings adjustments
    def set_prompts(self, prompt, negative_prompt=None):
        self.prompt = prompt
        self.negative_prompt = negative_prompt
    def set_inference_steps(self, steps):
        self.steps = steps 
    def set_CFG(self, CFG):
        self.CFG = CFG
    def set_height(self, height):
        self.height = height
    def set_width(self, width):
        self.width = width
    def set_seed(self, seed):
        self.seed = seed
    def set_image(self, image):
        self.image = image

    def gen_canny(self, image):
        image = np.array(image)
        image = cv2.Canny(image, 100, 200)
        image = image[:, :, None]
        image = np.concatenate([image, image, image], axis=2)
        canny_image = Image.fromarray(image)
        return canny_image        

    def setImage(self, image):
        self.image = image

# Main execution
if __name__ == "__main__":
    controlnet = ControlNetPipeline()
    generated_path = controlnet.generate_image(0)
    print(f"Generated image saved to {generated_path}")