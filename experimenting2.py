from diffusers.utils import load_image, make_image_grid

image = load_image("https://huggingface.co/datasets/diffusers/docs-images/resolve/main/t2i-adapter/color_ref.png")

from PIL import Image

color_palette = image.resize((8, 8))
color_palette = color_palette.resize((512, 512), resample=Image.Resampling.NEAREST)
import torch
from diffusers import StableDiffusionAdapterPipeline, T2IAdapter

adapter = T2IAdapter.from_pretrained("TencentARC/t2iadapter_color_sd14v1", torch_dtype=torch.float16)
pipe = StableDiffusionAdapterPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4",
    # "stabilityai/stable-diffusion-xl-base-1.0"
    adapter=adapter,
    torch_dtype=torch.float16,
)
pipe.to("cuda")
# fix the random seed, so you will get the same result as the example
generator = torch.Generator("cuda").manual_seed(7)

out_image = pipe(
    "At night, glowing cubes in front of the beach",
    image=color_palette,
    generator=generator,
).images[0]
out_image.save("color_palette.png")