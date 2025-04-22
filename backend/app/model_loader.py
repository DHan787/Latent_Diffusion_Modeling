import os

from diffusers import StableDiffusionPipeline
from peft import PeftModel
import torch

def load_model():
    model_id = "CompVis/stable-diffusion-v1-4"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    import os

    APP_DIR = os.path.dirname(os.path.abspath(__file__))

    # 找到项目根目录（再往上一级）
    PROJECT_ROOT = os.path.dirname(os.path.dirname(APP_DIR))

    # 构建 LoRA 权重所在目录
    lora_path = os.path.join(
        PROJECT_ROOT,
        "model", "Latent_Diffusion_model", "Latent_Diffusion_model", "sd-fine-tuned-lora"
    )

    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16 if device == "cuda" else torch.float32)
    pipe.to(device)
    pipe.safety_checker = None

    pipe.unet = PeftModel.from_pretrained(pipe.unet, lora_path)
    # pipe.enable_xformers_memory_efficient_attention()
    return pipe


def generate_image(pipe, prompt):
    image = pipe(prompt, num_inference_steps=30, guidance_scale=7.5).images[0]
    return image
