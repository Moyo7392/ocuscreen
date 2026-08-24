from __future__ import annotations

import asyncio
import io
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

import torch
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
from torch import nn
from torchvision import models, transforms

from .gradcam import GradCAM, hotspot_regions, overlay_data_url
from .quality_gate import assess_quality

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path(os.getenv("MODEL_PATH", ROOT / "models" / "model_best.pth"))
MAX_BYTES = 10 * 1024 * 1024
LABELS = ["No DR", "Mild NPDR", "Moderate NPDR", "Severe NPDR", "Proliferative DR"]
MODEL_VERSION = "1.0.0"
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
PREPROCESS = transforms.Compose([
    transforms.Resize((224, 224)), transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def build_model() -> nn.Module:
    model = models.efficientnet_b0(weights=None)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, 5)
    return model


def load_model() -> nn.Module:
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model checkpoint not found at {MODEL_PATH}. Train the model first.")
    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=False)
    state = checkpoint.get("model_state_dict", checkpoint)
    model = build_model()
    model.load_state_dict(state)
    return model.to(DEVICE).eval()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = load_model()
    app.state.gradcam = GradCAM(app.state.model, app.state.model.features[-1])
    app.state.inference_lock = asyncio.Lock()
    yield


app = FastAPI(title="OcuScreen Inference API", version=MODEL_VERSION, lifespan=lifespan)
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["GET", "POST"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION}


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    started_at = time.perf_counter()
    if image.content_type not in {"image/jpeg", "image/png"}:
        return JSONResponse(status_code=422, content={"error": "quality_rejection", "reason": "Upload a JPEG or PNG image."})
    payload = await image.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        return JSONResponse(status_code=413, content={"error": "file_too_large", "reason": "Image exceeds the 10 MB limit."})
    try:
        source = Image.open(io.BytesIO(payload)); source.load(); source = source.convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
        return JSONResponse(status_code=422, content={"error": "quality_rejection", "reason": "The upload is not a valid image."})
    quality = assess_quality(source)
    if not quality.accepted:
        return JSONResponse(status_code=422, content={"error": "quality_rejection", "reason": quality.reason})

    width, height = source.size
    tensor = PREPROCESS(source).unsqueeze(0).to(DEVICE)
    # Grad-CAM hooks keep request-local activation state, so serialize this short
    # critical section to prevent concurrent requests from mixing their maps.
    async with app.state.inference_lock:
        with torch.no_grad():
            logits = app.state.model(tensor)
            probabilities = torch.softmax(logits, dim=1)[0]
            grade = int(probabilities.argmax().item())
            confidence = float(probabilities[grade].item())
        cam = app.state.gradcam.generate(tensor, grade)
    probability_map = {str(index): round(float(value.item()), 4)
                       for index, value in enumerate(probabilities)}
    return {
        "grade": grade, "grade_label": LABELS[grade], "confidence": round(confidence, 4),
        "model_version": MODEL_VERSION, "heatmap_base64": overlay_data_url(source, cam),
        "probabilities": probability_map, "hotspots": hotspot_regions(cam),
        "image_metadata": {"width": width, "height": height, "file_size_bytes": len(payload)},
        "processing_time_ms": round((time.perf_counter() - started_at) * 1000),
        "quality_check": "Passed",
        "recommendation": ("Routine rescreening recommended." if grade <= 1
                           else "Referral to an ophthalmologist is advised."),
    }
