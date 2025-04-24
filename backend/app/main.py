from http.client import HTTPException

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

    if "," in req.image:
        base64_data = req.image.split(",")[1]
    else:
        base64_data = req.image

    with open(file_path, "wb") as f:
        f.write(base64.b64decode(base64_data))

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

@app.delete("/images/{image_id}")
def delete_image(image_id: str):
    image_path = os.path.join(GALLERY_DIR, f"{image_id}.png")

    # 删除图像文件
    if os.path.exists(image_path):
        os.remove(image_path)
    else:
        raise HTTPException(status_code=404, detail="Image file not found")

    # 删除元数据
    with open(METADATA_FILE, "r+") as f:
        data = json.load(f)
        if image_id in data:
            del data[image_id]
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
        else:
            raise HTTPException(status_code=404, detail="Image metadata not found")

    return {"success": True, "id": image_id}

@app.get("/images/{image_filename}")
def get_image(image_filename: str):
    file_path = os.path.join(GALLERY_DIR, image_filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="Image not found")