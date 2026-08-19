import { NextResponse } from "next/server";
import { GRADE_LABELS, recommendationFor } from "@/lib/clinical";
import { appendAudit, demoUserId, resultsStore } from "@/lib/demo-store";
import type { Grade, ScreeningResult } from "@/lib/types";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const MAX_SIZE = 10 * 1024 * 1024;
const TYPES = new Set(["image/jpeg", "image/png"]);

export async function POST(request: Request) {
  const userId = demoUserId(request);
  if (!userId) return NextResponse.json({ error: "unauthorized", reason: "A valid bearer token is required." }, { status: 401 });
  let form: FormData;
  try { form = await request.formData(); } catch { return NextResponse.json({ error: "invalid_request", reason: "Expected multipart form data." }, { status: 400 }); }
  const image = form.get("image");
  if (!(image instanceof File)) return NextResponse.json({ error: "invalid_request", reason: "An image file is required." }, { status: 400 });
  if (!TYPES.has(image.type) || image.size > MAX_SIZE) return NextResponse.json({ error: "invalid_file", reason: "Choose a JPEG or PNG image no larger than 10 MB." }, { status: 415 });

  const inferenceUrl = process.env.INFERENCE_SERVICE_URL;
  if (inferenceUrl && process.env.DEMO_MODE !== "true") {
    try {
      const upstream = new FormData(); upstream.append("image", image);
      const response = await fetch(`${inferenceUrl.replace(/\/$/, "")}/predict`, { method: "POST", body: upstream, signal: AbortSignal.timeout(55_000) });
      const payload = await response.json();
      if (!response.ok) return NextResponse.json(payload, { status: response.status });
      return persist(payload, image, userId);
    } catch {
      return NextResponse.json({ error: "inference_error", reason: "The grading service is temporarily unavailable. Please try again." }, { status: 500 });
    }
  }

  // Deterministic demo output exercises the full product without claiming clinical validity.
  const bytes = new Uint8Array(await image.arrayBuffer());
  const checksum = bytes.slice(0, 4096).reduce((sum, value) => (sum + value) % 100_003, 0);
  const grade = (checksum % 5) as Grade;
  return persist({ grade, grade_label: GRADE_LABELS[grade], confidence: .62 + (checksum % 30) / 100, model_version: "demo-1.0.0", recommendation: recommendationFor(grade) }, image, userId);
}

async function persist(payload: Omit<ScreeningResult, "id" | "timestamp" | "image_url" | "heatmap_url"> & { heatmap_base64?: string }, image: File, userId: string) {
  const id = crypto.randomUUID();
  const original = Buffer.from(await image.arrayBuffer()).toString("base64");
  const imageData = `data:${image.type};base64,${original}`;
  const result: ScreeningResult & { user_id: string; image_data?: string; heatmap_data?: string } = {
    id, user_id: userId, grade: payload.grade, grade_label: payload.grade_label,
    confidence: payload.confidence, model_version: payload.model_version,
    recommendation: payload.recommendation, timestamp: new Date().toISOString(),
    image_url: `/api/uploads/${id}`, heatmap_url: `/api/heatmaps/${id}`,
    image_data: imageData, heatmap_data: payload.heatmap_base64 ? `data:image/png;base64,${payload.heatmap_base64}` : imageData,
  };
  resultsStore.set(id, result);
  appendAudit({ user_id: userId, model_version: result.model_version, grade: result.grade, timestamp: result.timestamp });
  return NextResponse.json(result, { status: 200 });
}
