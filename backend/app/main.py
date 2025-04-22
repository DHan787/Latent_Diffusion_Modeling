from fastapi import FastAPI, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from uuid import uuid4
from datetime import datetime
from io import BytesIO
import os, base64, json
from PIL import Image
from model_loader import load_model, generate_image as run_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

GALLERY_DIR = "gallery_images"
METADATA_FILE = os.path.join(GALLERY_DIR, "metadata.json")
os.makedirs(GALLERY_DIR, exist_ok=True)

# === 初始化元数据 ===
if not os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "w") as f:
        json.dump({}, f)

# === 请求模型 ===
class PromptRequest(BaseModel):
    prompt: str

class SaveImageRequest(BaseModel):
    image: str  # base64
    prompt: str

# === 加载模型 ===
pipe = load_model()

# === 图像生成 API ===
@app.post("/generate")
def generate(req: PromptRequest):
    image = run_model(pipe, req.prompt)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return {"image_base64": img_str}

# === 保存图片 API ===
@app.post("/images")
def save_image(req: SaveImageRequest):
    image_id = str(uuid4())
    file_path = os.path.join(GALLERY_DIR, f"{image_id}.png")
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(req.image))

    with open(METADATA_FILE, "r+") as f:
        data = json.load(f)
        data[image_id] = {
            "prompt": req.prompt,
            "createdAt": datetime.now().isoformat()
        }
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    return {"success": True, "id": image_id, "url": f"/images/{image_id}.png"}

# === 列出图片 API ===
@app.get("/images")
def list_images():
    with open(METADATA_FILE, "r") as f:
        data = json.load(f)
    results = []
    for image_id, meta in data.items():
        results.append({
            "id": image_id,
            "url": f"/images/{image_id}.png",
            "prompt": meta["prompt"],
            "createdAt": meta["createdAt"]
        })
    return {"images": results}

# === 下载图片 API ===
@app.get("/images/{filename}")
def get_image(filename: str):
    path = os.path.join(GALLERY_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="image/png")
    return {"error": "Image not found"}