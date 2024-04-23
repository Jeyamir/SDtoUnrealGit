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


class AdapterPipeline:
    def __init__(self):

        
        self.set_padding(padding_mode='circular')
        self.load_models()
        self.save_settings()
        # Pre-compile the model for faster inference if using TorchScript
        # self.base.unet = torch.compile(self.base.unet, mode="reduce-overhead", fullgraph=True)
        self.load_default_settings()

    def load_models(self):
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        adapter = T2IAdapter.from_pretrained("TencentARC/t2i-adapter-canny-sdxl-1.0", torch_dtype=torch.float16, varient="fp16").to("cuda")
        scheduler = DDPMScheduler.from_pretrained(model_id, subfolder="scheduler")
        euler_a = EulerAncestralDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
        vae=AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
        self.pipe = StableDiffusionXLAdapterPipeline.from_pretrained(
    model_id, vae=vae, adapter=adapter, scheduler=euler_a, torch_dtype=torch.float16, variant="fp16", 
).to("cuda")
        self.pipe.to("cuda")


    def generate_image(self, index):
        # Run both experts
        compel_proc = Compel(tokenizer=self.pipe.tokenizer, text_encoder=self.pipe.text_encoder)
        prompt_embeds = compel_proc(self.prompt)
        self.prompt = self.prompt.strip()

        url = "https://huggingface.co/Adapter/t2iadapter/resolve/main/figs_SDXLV1.0/org_canny.jpg"
        image = load_image(url)
        canny_detector = CannyDetector()
        # Detect the canny map in low resolution to avoid high-frequency details
        image = canny_detector(image, detect_resolution=384, image_resolution=1024)#.resize((1024, 1024))

        # generator = torch.Generator().manual_seed(self.seed + index)
        sketch_image_out = self.pipe(
            prompt="Mystical fairy in real, magic, 4k picture, high quality",
            negative_prompt="extra digit, fewer digits, cropped, worst quality, low quality",
            image=image
            # generator=generator,
            # guidance_scale=7.5,
            # num_inference_steps=30,
            # adapter_conditioning_scale=0.8
        ).images[0]

        file_path = f"./{self.prompt[:30]}_{index}.png".replace("\n", "")
        sketch_image_out.save("sketch_image_out.png")
        self.preimage.save("sketch_image.png")
        return file_path
    

    def load_default_settings(self):
        self.set_prompts("a photo of a dog in real world, high quality", "extra digit, fewer digits, cropped, worst quality, low quality")
        self.set_preimage(load_image("https://huggingface.co/Adapter/t2iadapter/resolve/main/figs_SDXLV1.0/org_canny.jpg"))
                        #   .convert("L"))
        self.set_padding(padding_mode='circular')
        self.set_inference_steps(20)

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

    
    def set_prompts(self, prompt, negative_prompt = None):
        self.prompt = prompt
        self.negative_prompt = negative_prompt

    def set_padding(self, **patch):
        cls = torch.nn.Conv2d
        init = cls.__init__
        def __init__(self, *args, **kwargs):
            return init(self, *args, **kwargs, **patch)
        cls.__init__ = __init__

    def set_inference_steps(self, steps):
        self.steps = steps
    def set_CFG(self, CFG):
        self.CFG = CFG
    def set_seed(self, seed):
        self.seed = seed

    def set_preimage(self, image):
        self.preimage = image
        canny_detector = CannyDetector()
        self.preimage = canny_detector(self.preimage, detect_resolution=384, image_resolution=1024)
    
if __name__ == "__main__":
    adapter = AdapterPipeline()
    adapter.set_prompts("a photo of a dog in real world, high quality", "extra digit, fewer digits, cropped, worst quality, low quality")
    adapter.generate_image(0)
    adapter.save_settings()
