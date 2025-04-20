from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
import base64, io, os, subprocess, shlex, datetime
from typing import Optional, Dict

from diffusion import get_pipeline, generate_image
from fine_tune import launch_fine_tune, JobStatus, job_registry

app = FastAPI(title="Stable‑Diffusion Backend", version="1.0.0")

# CORS so that any front‑end (React / Next.js / etc.) can call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------
# Schemas
# ---------------------
class GenerateRequest(BaseModel):
    prompt: str
    num_inference_steps: int = 30
    guidance_scale: float = 7.5
    height: int = 512
    width: int = 512
    seed: Optional[int] = None

class GenerateResponse(BaseModel):
    request_id: str
    image_base64: str  # PNG base64 string (front‑end turns it into <img src="data:image/png;base64,…">)

class FineTuneRequest(BaseModel):
    dataset_name: str              # e.g. "lambdalabs/naruto-blip-captions"
    output_dir: str                # where to write checkpoints /logs
    max_train_steps: int = 1000
    learning_rate: float = 1e-6

class FineTuneResponse(BaseModel):
    job_id: str
    message: str

class FineTuneStatus(BaseModel):
    job_id: str
    state: JobStatus
    started_at: Optional[datetime.datetime]
    finished_at: Optional[datetime.datetime]
    progress: Optional[str]

# ---------------------
# Routes
# ---------------------
@app.post("/generate", response_model=GenerateResponse)
async def generate_endpoint(body: GenerateRequest):
    pipeline = get_pipeline()  # lazy‑loaded, cached

    try:
        image = await generate_image(
            pipeline,
            prompt=body.prompt,
            num_inference_steps=body.num_inference_steps,
            guidance_scale=body.guidance_scale,
            height=body.height,
            width=body.width,
            seed=body.seed,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # convert to b64 PNG
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return GenerateResponse(request_id=str(uuid4()), image_base64=img_str)


@app.post("/fine_tune", response_model=FineTuneResponse)
async def fine_tune_endpoint(body: FineTuneRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    background_tasks.add_task(
        launch_fine_tune,
        job_id=job_id,
        dataset_name=body.dataset_name,
        output_dir=body.output_dir,
        max_train_steps=body.max_train_steps,
        learning_rate=body.learning_rate,
    )
    return FineTuneResponse(job_id=job_id, message="Fine‑tuning started in background")


@app.get("/fine_tune/{job_id}", response_model=FineTuneStatus)
async def fine_tune_status(job_id: str):
    status = job_registry.get(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return status


# =====================
# app/diffusion.py
# =====================
from diffusers import StableDiffusionPipeline
from torch import cuda, Generator
import torch, asyncio

_MODEL_ID = "runwayml/stable-diffusion-v1-5"  # change if you fine‑tune and want to load new weights
_DEVICE = "cuda" if cuda.is_available() else "cpu"
_PIPE = None  # cached global


def get_pipeline():
    global _PIPE
    if _PIPE is None:
        dtype = torch.float16 if _DEVICE == "cuda" else torch.float32
        _PIPE = StableDiffusionPipeline.from_pretrained(_MODEL_ID, torch_dtype=dtype)
        _PIPE.to(_DEVICE)
        _PIPE.safety_checker = None  # disable NSFW filtering; add your own if needed
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