from diffusers import StableDiffusionPipeline
from peft import PeftModel
from torch import cuda, Generator
import torch
from PIL import Image

BASE_MODEL = "CompVis/stable-diffusion-v1-4"
LORA_PATH = "../../model/Latent_Diffusion_model/Latent_Diffusion_model/sd-fine-tuned-lora"
DEVICE = "cuda" if cuda.is_available() else "cpu"

def get_pipeline():
    dtype = torch.float16 if DEVICE == "cuda" else torch.float32

    # 加载 base 模型
    pipe = StableDiffusionPipeline.from_pretrained(BASE_MODEL, torch_dtype=dtype)
    pipe.to(DEVICE)
    pipe.safety_checker = None

    # 正确加载 LoRA adapter（替换 U-Net）
    pipe.unet = PeftModel.from_pretrained(pipe.unet, LORA_PATH)
    pipe.unet.eval()

    pipe.enable_attention_slicing()
    return pipe

def generate_image(pipeline, prompt, seed=42, height=512, width=512, steps=25, scale=7.5):
    generator = Generator(DEVICE).manual_seed(seed)
    result = pipeline(
        prompt,
        num_inference_steps=steps,
        guidance_scale=scale,
        height=height,
        width=width,
        generator=generator,
    )
    return result.images[0]

if __name__ == "__main__":
    pipe = get_pipeline()
    prompt = "A man in red shirt and blue jeans standing in a field of flowers, sunny day"
    image = generate_image(pipe, prompt)
    image.save("test_output.png")
    print("Saved as test_output.png")
