import base64
import os
import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from model import RetinopathyModel
from preprocessing import to_tensor
from quality_gate import assess_quality
from gradcam import GradCAM, overlay_heatmap

LABELS = ["No apparent DR", "Mild NPDR", "Moderate NPDR", "Severe NPDR", "Proliferative DR"]
app = FastAPI(title="OcuScreen Inference Service", version="1.0.0")
model: RetinopathyModel | None = None

@app.on_event("startup")
def load_model():
    global model
    if os.getenv("SKIP_MODEL_LOAD", "false").lower() != "true": model = RetinopathyModel()

@app.get("/health")
def health(): return {"status": "ok" if model else "model_unavailable", "model_version": model.version if model else None}

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    if image.content_type not in {"image/jpeg", "image/png"}: raise HTTPException(415, {"error": "invalid_file", "reason": "Only JPEG and PNG images are accepted."})
    payload = await image.read(10 * 1024 * 1024 + 1)
    if len(payload) > 10 * 1024 * 1024: raise HTTPException(413, {"error": "invalid_file", "reason": "Image must be 10 MB or smaller."})
    frame = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR)
    if frame is None: raise HTTPException(415, {"error": "invalid_file", "reason": "The uploaded file is not a valid image."})
    quality = assess_quality(frame)
    if not quality.accepted: raise HTTPException(422, {"error": "quality_rejection", "reason": quality.reason})
    if model is None: raise HTTPException(503, {"error": "inference_error", "reason": "Model artifact is not loaded."})
    tensor = to_tensor(frame).to(model.device)
    grade, confidence, _ = model.predict(tensor)
    cam = GradCAM(model.model, model.target_layer)
    try: attention = cam.generate(tensor, grade)
    finally: cam.close()
    encoded = cv2.imencode(".png", overlay_heatmap(frame, attention))[1].tobytes()
    return {"grade": grade, "grade_label": LABELS[grade], "confidence": confidence, "model_version": model.version, "heatmap_base64": base64.b64encode(encoded).decode(), "recommendation": "Routine rescreening recommended." if grade <= 1 else "Referral to an ophthalmologist is advised."}
