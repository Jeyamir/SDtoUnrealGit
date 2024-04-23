import torch
from diffusers import DiffusionPipeline, DDIMScheduler, KDPM2DiscreteScheduler, PNDMScheduler, DPMSolverSDEScheduler, EulerAncestralDiscreteScheduler, DDPMScheduler, DEISMultistepScheduler, DPMSolverMultistepScheduler, KDPM2AncestralDiscreteScheduler, EDMEulerScheduler, HeunDiscreteScheduler, LMSDiscreteScheduler, EulerDiscreteScheduler, UniPCMultistepScheduler, DPMSolverSinglestepScheduler
from PySide6.QtCore import QSettings
from compel import Compel

# from diffusers.pipelines.stable_diffusion import StableDiffusionSafetyChecker
from random import randint
import re
# from accelerate import Accelerator

class SDXLPipeline:
    def __init__(self, model = "stabilityai/stable-diffusion-xl-refiner-1.0"):

        
        self.set_padding(padding_mode='circular')

        self.load_models()
        self.save_settings()
        # Pre-compile the model for faster inference if using TorchScript
        # self.base.unet = torch.compile(self.base.unet, mode="reduce-overhead", fullgraph=True)
        self.load_default_settings()

    def load_models(self):
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        # "dream-textures/texture-diffusion"
        # "stabilityai/stable-diffusion-xl-base-1.0"
        self.base = DiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16",
        )
        # .to("cuda")
        self.base.enable_model_cpu_offload()

        self.refiner = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-refiner-1.0",
            text_encoder_2=self.base.text_encoder_2,
            vae=self.base.vae,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16",
            )
            # .to("cuda")
        self.refiner.enable_model_cpu_offload()

    def generate_image(self, index):
        # Run both experts
        compel_proc = Compel(tokenizer=self.base.tokenizer, text_encoder=self.base.text_encoder)
        self.prompt = self.prompt.strip()
        prompt_embeds = compel_proc(self.prompt)
        generator = torch.Generator().manual_seed(self.seed + index)
        if self.refinerBool:
            image = self.base(
                prompt_embeds=prompt_embeds,
                negative_prompt = self.negative_prompt,
                num_inference_steps=self.steps,
                denoising_end=self.denoising_fraction,
                guidance_scale = self.CFG,
                height = self.height,
                width = self.width,
                generator = generator,
                output_type="latent",
            ).images

            image = self.refiner(
                prompt_embeds = prompt_embeds,
                negative_prompt = self.negative_prompt,
                num_inference_steps=self.steps,
                denoising_start=self.denoising_fraction,
                guidance_scale = self.CFG,
                height = self.height,
                width = self.width,
                generator = generator,
                image=image,
            ).images[0]

        else:
            image = self.base(
                prompt = self.prompt,
                negative_prompt = self.negative_prompt,
                num_inference_steps=self.steps,
                denoising_end=1.0,
                guidance_scale = self.CFG,
                height = self.height,
                width = self.width,
                generator = generator,
            ).images[0]

        file_path = f"./{self.prompt[:30]}_{index}.png".replace("\n", "")
        image.save(file_path)
        return file_path
    

    def load_default_settings(self):
        self.set_prompts()
        self.set_inference_steps(30)
        self.set_denoising_fraction(.8)
        self.set_CFG(5.0)
        self.set_height(1024)
        self.set_width(1024)
        self.set_seed(randint(1, 999999))
        self.set_refiner(False)
  

    # load all the schedulers
    def set_scheduler(self, scheduler_str):
        if(scheduler_str == "DDIMScheduler"):
            self.base.scheduler = DDIMScheduler.from_config(self.base.scheduler.config)
            print("Scheduler set to DDIMScheduler")
        elif(scheduler_str == "KDPM2DiscreteScheduler"):
            self.base.scheduler = KDPM2DiscreteScheduler.from_config(self.base.scheduler.config)
            print("Scheduler set to KDPM2DiscreteScheduler")
        elif(scheduler_str == "PNDMScheduler"):
            self.base.scheduler = PNDMScheduler.from_config(self.base.scheduler.config)
            print("Scheduler set to PNDMScheduler")
        elif(scheduler_str == "DPMSolverSDEScheduler"):
            self.base.scheduler = DPMSolverSDEScheduler.from_config(self.base.scheduler.config)
            print("Scheduler set to DPMSolverSDEScheduler")
        elif(scheduler_str == "EulerAncestralDiscreteScheduler"):
            self.base.scheduler = EulerAncestralDiscreteScheduler.from_config(self.base.scheduler.config)
            print("Scheduler set to EulerAncestralDiscreteScheduler")
        elif(scheduler_str == "DDPMScheduler"):
            print("Scheduler set to DDPMScheduler")
            self.base.scheduler = DDPMScheduler.from_config(self.base.scheduler.config)
        elif(scheduler_str == "DEISMultistepScheduler"):
            print("Scheduler set to DEISMultistepScheduler")
            self.base.scheduler = DEISMultistepScheduler.from_config(self.base.scheduler.config)
        elif(scheduler_str == "DPMSolverMultistepScheduler"):
            print("Scheduler set to DPMSolverMultistepScheduler")
            self.base.scheduler = DPMSolverMultistepScheduler.from_config(self.base.scheduler.config)
        elif(scheduler_str == "KDPM2AncestralDiscreteScheduler"):
            print("Scheduler set to KDPM2AncestralDiscreteScheduler")
            self.base.scheduler = KDPM2AncestralDiscreteScheduler.from_config(self.base.scheduler.config)
        elif(scheduler_str == "EDMEulerScheduler"):
            print("Scheduler set to EDMEulerScheduler")
            self.base.scheduler = EDMEulerScheduler.from_config(self.base.scheduler.config)
        elif(scheduler_str == "HeunDiscreteScheduler"):
            print("Scheduler set to HeunDiscreteScheduler")
            self.base.scheduler = HeunDiscreteScheduler.from_config(self.base.scheduler.config)
        elif(scheduler_str == "LMSDiscreteScheduler"):
            print("Scheduler set to LMSDiscreteScheduler")
            self.base.scheduler = LMSDiscreteScheduler.from_config(self.base.scheduler.config)
        elif(scheduler_str == "EulerDiscreteScheduler"):
            print("Scheduler set to EulerDiscreteScheduler")
            self.base.scheduler = EulerDiscreteScheduler.from_config(self.base.scheduler.config)
        elif(scheduler_str == "UniPCMultistepScheduler"):
            print("Scheduler set to UniPCMultistepScheduler")
            self.base.scheduler = UniPCMultistepScheduler.from_config(self.base.scheduler.config)
        elif(scheduler_str == "DPMSolverSinglestepScheduler"):
            print("Scheduler set to DPMSolverSinglestepScheduler")
            self.base.scheduler = DPMSolverSinglestepScheduler.from_config(self.base.scheduler.config)
        else:
            ...

    # saving qsettings for the UI
    def save_settings(self):
        self.settings = QSettings("Ashill", "SDtoUnreal")
        pattern = r'(?<=\.)([^.]*?)\'>'
        compatible_schedulers = []
        for scheduler in list(self.base.scheduler.compatibles):
            scheduler_name = str(scheduler)
            match = re.search(pattern, scheduler_name)
            if match:
                result = match.group(1)
                compatible_schedulers.append(result)
        self.settings.setValue("SchedulersList",list(compatible_schedulers))
        

    def set_prompts(self, prompt = "default", negative_prompt = None):
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
    def set_denoising_fraction(self, fraction):
        self.denoising_fraction = fraction
    def set_CFG(self, CFG):
        self.CFG = CFG
    def set_height(self, height):
        self.height = height
    def set_width(self, width):
        self.width = width
    def set_seed(self, seed):
        self.seed = seed
    def set_refiner(self, state):
        self.refinerBool = state
        print(f"Refiner set to {state}")
