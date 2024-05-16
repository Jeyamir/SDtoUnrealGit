import torch
from diffusers import (
    T2IAdapter,
    StableDiffusionXLAdapterPipeline,
    DDPMScheduler, 
    EulerAncestralDiscreteScheduler,
    AutoencoderKL
)
from diffusers.utils import load_image, make_image_grid
from compel import Compel
from PySide6.QtCore import QSettings
import re
from controlnet_aux.canny import CannyDetector
from diffusers.utils import load_image
from random import randint
import utils_adapters


class AdapterPipeline:
    def __init__(self):

        
        self.set_padding(padding_mode='circular')
        # Pre-compile the model for faster inference if using TorchScript
        # self.base.unet = torch.compile(self.base.unet, mode="reduce-overhead", fullgraph=True)

    def load_models(self, model = "Canny"):
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        if model == "Canny":
            self.adapter = T2IAdapter.from_pretrained("TencentARC/t2i-adapter-canny-sdxl-1.0", torch_dtype=torch.float16, varient="fp16").to("cuda")
        elif model == "Sketch/Scribble":
            self.adapter = T2IAdapter.from_pretrained("TencentARC/t2i-adapter-sketch-sdxl-1.0", torch_dtype=torch.float16, varient="fp16").to("cuda")
        elif model == "Depth":
            self.adapter = T2IAdapter.from_pretrained("TencentARC/t2i-adapter-depth-midas-sdxl-1.0", torch_dtype=torch.float16, varient="fp16").to("cuda")
        elif model == "Lineart":
            self.adapter = T2IAdapter.from_pretrained("TencentARC/t2i-adapter-lineart-sdxl-1.0", torch_dtype=torch.float16, varient="fp16").to("cuda")
        elif model == "OpenPose":
            self.adapter = T2IAdapter.from_pretrained("TencentARC/t2i-adapter-openpose-sdxl-1.0", torch_dtype=torch.float16, varient="fp16").to("cuda")
        else:
            self.adapter = T2IAdapter.from_pretrained("TencentARC/t2i-adapter-canny-sdxl-1.0", torch_dtype=torch.float16, varient="fp16").to("cuda")



        scheduler = DDPMScheduler.from_pretrained(model_id, subfolder="scheduler")
        euler_a = EulerAncestralDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
        vae=AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
        self.pipe = StableDiffusionXLAdapterPipeline.from_pretrained(
        model_id, vae=vae, adapter=self. adapter, scheduler=euler_a, torch_dtype=torch.float16, variant="fp16", 
        ).to("cuda")

        self.pipe.to("cuda")


    def generate_image(self):
        # Run both experts
        if self.generatesettings and self.seed and self.condition_image:
            compel_proc = Compel(tokenizer=self.pipe.tokenizer, text_encoder=self.pipe.text_encoder)
            self.generatesettings["prompt"] = self.generatesettings["prompt"].strip()
            # conditioning, pooled = compel_proc(self.generatesettings["prompt"])
            if not self.seed:
                self.seed = randint(1, 999999)
            generator = torch.Generator().manual_seed(self.seed)

            sketch_image_out = self.pipe(
                prompt = "neon blocks on the beach",
                # prompt_embeds=conditioning,
                # pooled_prompt_embeds=pooled,
                negative_prompt=self.generatesettings["negativePrompt"],
                image=self.condition_image,
                generator=generator,
                height=self.generatesettings["height"],
                width=self.generatesettings["width"],
                guidance_scale=self.generatesettings["CFG"],
                num_inference_steps=self.generatesettings["numInferenceSteps"],
                adapter_conditioning_scale=self.generatesettings["adapterConditioningScale"],
                adapter_conditioning_factor=self.generatesettings["adapterConditioningFactor"],
                num_images_per_prompt=self.generatesettings["numImagesPerPrompt"]
            ).images[0]

            # file_path = f"./{self.generatesettings["prompt"][:30]}_1.png".replace("\n", "")
            sketch_image_out.save("sketch_image_out.png")
            # return file_path


    def save_settings(self):
        self.settings = QSettings("Ashill", "SDtoUnreal")
        pattern = r'(?<=\.)([^.]*?)\'>'
        compatible_schedulers = []
        for scheduler in list(self.pipe.scheduler.compatibles):
            scheduler_name = str(scheduler)
            match = re.search(pattern, scheduler_name)
            if match:
                result = match.group(1)
                compatible_schedulers.append(result)
        self.settings.setValue("AdapterSchedulersList",list(compatible_schedulers))




    #setting the parameters for pipe
    #options are: prompt, negative_prompt, padding, inference_steps, CFG, seed, adapter_conditioning_scale, adapter_conditioning_factor, num_images_per_prompt
    def set_adapter_type(self, adapter_type):
        self.load_models(adapter_type)
        self.save_settings()

    def set_image(self, image_path, is_canny=False):
        self.condition_image = load_image(image_path)

        if is_canny:
            self.condition_image = utils_adapters.calc_canny_image(self.condition_image, resolution=1024)
        return self.condition_image

    def set_padding(self, **patch):
        cls = torch.nn.Conv2d
        init = cls.__init__
        def __init__(self, *args, **kwargs):
            return init(self, *args, **kwargs, **patch)
        cls.__init__ = __init__

    def set_settings(self, settingsDict):
        self.generatesettings = settingsDict

    def set_seed(self, seed):
        self.seed = seed
    
if __name__ == "__main__":
    adapter = AdapterPipeline()
    adapter.set_prompts("a photo of a dog in real world, high quality", "extra digit, fewer digits, cropped, worst quality, low quality")
    adapter.generate_image(0)
    adapter.save_settings()
