# OcuScreen

OcuScreen is an AI-assisted diabetic retinopathy screening and triage demo for the UT Arlington CSE 4316 Retinauts team. It returns a five-level severity grade, model confidence, Grad-CAM visualization, and referral advisory. It is explicitly decision support—not a diagnostic device.

## Run the working demo

```bash
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`, select **Sign in as Demo User**, then upload a JPEG or PNG. `DEMO_MODE=true` runs a deterministic, non-clinical stub so the complete upload/result/history/PDF workflow can be demonstrated without a multi-gigabyte model artifact. The stub's model version is visibly labeled `demo-1.0.0`; its heatmap is only a presentation placeholder.

Records and the append-only audit stream use process memory in demo mode and reset when the Next.js process or serverless instance restarts. This is intentional for a zero-configuration course demo. Production deployment should replace `lib/demo-store.ts` with Firestore or Supabase repositories and replace `demoUserId()` with server-side Firebase/Supabase token verification. The API already enforces ownership when reading records.

## Run the inference service

Place the trained checkpoint at `inference/artifacts/efficientnet_b0_aptos.pt` (or set `MODEL_WEIGHTS`) and set a version string:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r inference/requirements.txt
MODEL_WEIGHTS=inference/artifacts/efficientnet_b0_aptos.pt MODEL_VERSION=1.0.0 \
  uvicorn app:app --app-dir inference --reload --port 8000
```

Then set `DEMO_MODE=false` and `INFERENCE_SERVICE_URL=http://localhost:8000` in `.env.local`. The service rejects invalid, small, poorly shaped, blurry, dark, overexposed, or non-retinal-field images before inference. A missing model artifact fails startup rather than silently using random weights.

Health check: `GET /health`. Inference: `POST /predict` with multipart field `image`.

## Train on APTOS 2019

Put `train.csv` and images under `data/aptos`, adjust [training/config.yaml](training/config.yaml), and run:

```bash
pip install -r training/requirements.txt
python training/train.py --config training/config.yaml
```

Training uses ImageNet-pretrained EfficientNet-B0, a five-class head, inverse-frequency class weights, stratified 80/20 splitting, augmentation, Adam, cosine annealing, and best-checkpoint selection by validation quadratic-weighted kappa. A reported QWK must be independently measured on held-out data; this repository does not claim the target has been reached without a trained artifact and evaluation output.

## Deployment

- Deploy the repository to Vercel; HTTPS is automatic. Configure `INFERENCE_SERVICE_URL`, `DEMO_MODE=false`, `LOW_CONFIDENCE_THRESHOLD`, and production auth/database secrets in its dashboard.
- Build `inference/Dockerfile` on Railway or Render and configure `MODEL_WEIGHTS`/`MODEL_VERSION`. Store the versioned artifact in persistent storage or bake it into a private deployment image.
- Never commit model weights, credentials, retinal images, or patient identifiers.

## Verification

```bash
npm test
npm run build
python3 -m compileall -q inference training
```

The UI is keyboard operable, responsive, uses text alongside severity colors, and renders the mandatory non-diagnostic disclaimer on every result and in every PDF export.
