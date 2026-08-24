# OcuScreen

OcuScreen is an AI-assisted diabetic retinopathy screening and triage prototype by **Retinauts** for **CSE 4316 Senior Design at UT Arlington**. A clinician uploads a retinal fundus photograph and receives a 0–4 severity grade, model confidence, Grad-CAM attention overlay, and referral recommendation.

> OcuScreen is a decision-support and triage aid. It is not an FDA-cleared diagnostic device and does not replace examination by a licensed clinician.

The application intentionally collects no patient identifiers. Demo history is stored only in the current browser.

See the [model card](docs/model-card.md) for evaluation results, data-leakage caveats, intended use, and limitations. Retinal reference images with unclear redistribution rights are intentionally excluded from this public release.

## Requirements

- Node.js 20+
- Python 3.10+ (3.12 recommended)
- Kaggle API credentials for the APTOS dataset

On macOS: `brew install node python@3.12`.

## 1. Dataset and Python environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt kaggle
mkdir -p data
kaggle competitions download -c aptos2019-blindness-detection -p data
unzip data/aptos2019-blindness-detection.zip -d data
rm data/aptos2019-blindness-detection.zip
```

Place `kaggle.json` at `~/.kaggle/kaggle.json` with mode `600` first. The expected inputs are `data/train.csv` and `data/train_images/*.png`. Dataset and model files are gitignored.

## 2. Train

```bash
source .venv/bin/activate
python training/train.py
```

The default run uses 25 epochs, freezes the pretrained EfficientNet-B0 backbone for the first five, then fine-tunes the full network. The best quadratic-weighted kappa checkpoint is written to `models/model_best.pth`. Use `--batch-size 16` if memory is constrained. Training time and QWK vary by hardware and split; the target is not guaranteed.

## 3. Run inference

```bash
source .venv/bin/activate
uvicorn inference.app:app --host 0.0.0.0 --port 8000
```

Health check: `curl http://localhost:8000/health`

Prediction:

```bash
curl -X POST -F "image=@data/train_images/000c1434d8d7.png" http://localhost:8000/predict
```

The service fails fast at startup if the trained checkpoint is absent. Configure comma-separated browser origins with `CORS_ORIGINS` and an alternate checkpoint with `MODEL_PATH`.

## 4. Run frontend

```bash
cd app
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`, sign in as the demo user, upload a JPEG/PNG under 10 MB, and analyze it.

## Verification

```bash
source .venv/bin/activate
pytest
cd app && npm run typecheck && npm run build
```

## Deployment

Deploy `app/` to Vercel and set `NEXT_PUBLIC_INFERENCE_URL` to the public inference URL. Build the inference container from the repository root so Docker can include both `inference/` and `models/model_best.pth`:

```bash
docker build -f inference/Dockerfile -t ocuscreen-inference .
docker run -p 8000:8000 -e CORS_ORIGINS=https://your-app.vercel.app ocuscreen-inference
```

Deploy that image to Railway or Render. The model is excluded from Git by design; provide it through a private artifact/build process rather than committing it.
