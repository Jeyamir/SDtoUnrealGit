import torch
from diffusers import DiffusionPipeline, UNet2DConditionModel, DDIMScheduler, KDPM2DiscreteScheduler, PNDMScheduler, DPMSolverSDEScheduler, EulerAncestralDiscreteScheduler, DDPMScheduler, DEISMultistepScheduler, DPMSolverMultistepScheduler, KDPM2AncestralDiscreteScheduler, EDMEulerScheduler, HeunDiscreteScheduler, LMSDiscreteScheduler, EulerDiscreteScheduler, UniPCMultistepScheduler, DPMSolverSinglestepScheduler
from PySide6.QtCore import QSettings
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
from compel import Compel, ReturnedEmbeddingsType

# from diffusers.pipelines.stable_diffusion import StableDiffusionSafetyChecker
from random import randint
import re
# from accelerate import Accelerator

class SDXLPipeline:
    def __init__(self):

        
        self.set_refiner(False)


    def load_models(self, loadSettings):
        if loadSettings["tiling"] == "True":
            self.set_padding(padding_mode="circular")
        else:
            self.set_padding(padding_mode="zeros")


        self.base = None
        self.refiner = None
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        if loadSettings['model'] == "Stable Diffusion XL Lightning":
            print("Loading lightning checkpoint")
            repo = "ByteDance/SDXL-Lightning"
            ckpt = "sdxl_lightning_4step_unet.safetensors"
            unet_config = UNet2DConditionModel.load_config(model_id, subfolder="unet")
            # Instantiate the model from its configuration.
            unet = UNet2DConditionModel.from_config(unet_config).to("cuda", torch.float16)
            # Load the model's weights.
            unet.load_state_dict(load_file(hf_hub_download(repo, ckpt), device="cuda"))

            # Create a pipeline with the model.
            self.base = DiffusionPipeline.from_pretrained(model_id, unet=unet, torch_dtype=torch.float16, variant="fp16")

        else:
            print("Loading base and refiner models")
            self.base = DiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                use_safetensors=True,
                variant="fp16",
            )
            # .to("cuda")
            self.base.enable_model_cpu_offload()

            self.refiner = DiffusionPipeline.from_pretrained(
                model_id,
                text_encoder_2=self.base.text_encoder_2,
                # vae=self.base.vae,
                torch_dtype=torch.float16,
                use_safetensors=True,
                variant="fp16",
                )
            self.refiner.enable_model_cpu_offload()
        self.base.enable_model_cpu_offload()
        self.save_settings()

    def generate_image(self, index):
        # compel = Compel(
        # tokenizer=[self.base.tokenizer, self.base.tokenizer_2] ,
        # text_encoder=[self.base.text_encoder, self.base.text_encoder_2],
        # returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED,
        # requires_pooled=[False, True]
        # )
        # conditioning_embeds, pooled_embeds = compel(self.generateSettings["prompt"])
        self.prompt = self.generateSettings["prompt"].strip()
        generator = torch.Generator().manual_seed(self.generateSettings["seed"] + index)
        if self.refinerBool:
            image = self.base(
                # prompt_embeds=conditioning_embeds,
                # pooled_prompt_embeds=pooled_embeds,
                prompt = self.prompt,
                negative_prompt = self.generateSettings["negativePrompt"],
                num_inference_steps=self.generateSettings["numInferenceSteps"],
                denoising_end=self.generateSettings["denoisingEnd"],
                guidance_scale = self.generateSettings["CFG"],
                height = self.generateSettings["height"],
                width = self.generateSettings["width"],
                generator = generator,
                output_type="latent",
            ).images

            image = self.refiner(
                # prompt_embeds=conditioning_embeds,
                # pooled_prompt_embeds=pooled_embeds,
                prompt = self.prompt,
                negative_prompt = self.generateSettings["negativePrompt"],
                num_inference_steps= self.generateSettings["numInferenceSteps"],
                denoising_start= self.generateSettings["denoisingEnd"],
                guidance_scale = self.generateSettings["CFG"],
                height = self.generateSettings["height"],
                width =  self.generateSettings["width"],
                generator = generator,
                image=image,
            ).images[0]
            
        else:
            image = self.base(
                # prompt_embeds=conditioning_embeds,
                # pooled_prompt_embeds=pooled_embeds,
                prompt = self.prompt,
                negative_prompt = self.generateSettings["negativePrompt"],
                num_inference_steps=self.generateSettings["numInferenceSteps"],
                guidance_scale = self.generateSettings["CFG"],
                height =  self.generateSettings["height"],
                width = self.generateSettings["width"],
                generator = generator,
            ).images[0]

        file_path = f"./{self.prompt[:30]}_{index}.png".replace("\n", "")
        image.save(file_path)
        return file_path
    

    # load all the schedulers
    def set_scheduler(self, scheduler_str):
        if(scheduler_str == "DDIMScheduler"):
            self.base.scheduler = DDIMScheduler.from_config(self.base.scheduler.config)
            print("Scheduler set to DDIMScheduler")
        elif(scheduler_str == "KDPM2DiscreteScheduler"):
            self.base.scheduler = KDPM2DiscreteScheduler.from_config(self.base.scheduler.config, )
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
            self.base.scheduler = EulerDiscreteScheduler.from_config(self.base.scheduler.config, timestep_spacing="trailing")
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

    def set_padding(self, **patch):
        cls = torch.nn.Conv2d
        init = cls.__init__

        def __init__(self, *args, **kwargs):
            kwargs.update(patch)  # Merge patch values into kwargs
            return init(self, *args, **kwargs)

        cls.__init__ = __init__
    
    def set_settings(self, settingsDict):
        self.generateSettings = settingsDict
    
    def set_refiner(self, refinerBool):
        self.refinerBool = refinerBool



