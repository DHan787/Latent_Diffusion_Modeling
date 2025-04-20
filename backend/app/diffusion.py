from diffusers import StableDiffusionPipeline
from torch import cuda, Generator
import torch, asyncio

_MODEL_ID = "PLACE_HOLDER"
_DEVICE = "cuda" if cuda.is_available() else "cpu"
_PIPE = None  # cached global


def get_pipeline():
    global _PIPE
    if _PIPE is None:
        dtype = torch.float16 if _DEVICE == "cuda" else torch.float32
        _PIPE = StableDiffusionPipeline.from_pretrained(_MODEL_ID, torch_dtype=dtype)
        _PIPE.to(_DEVICE)
        _PIPE.safety_checker = None
    return _PIPE


async def generate_image(pipeline: StableDiffusionPipeline, **kwargs):
    # run in a threadpool to avoid blocking event‑loop
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_generate, pipeline, kwargs)


def _sync_generate(pipeline, kwargs):
    generator = None
    if kwargs.get("seed") is not None:
        generator = Generator(_DEVICE).manual_seed(kwargs["seed"])
    image = pipeline(
        kwargs["prompt"],
        num_inference_steps=kwargs["num_inference_steps"],
        guidance_scale=kwargs["guidance_scale"],
        height=kwargs["height"],
        width=kwargs["width"],
        generator=generator,
    ).images[0]
    return image