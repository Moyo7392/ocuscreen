import axios from "axios";
import type { Prediction } from "./types";

const baseURL = process.env.NEXT_PUBLIC_INFERENCE_URL || "http://localhost:8000";

export async function analyzeImage(file: File): Promise<Prediction> {
  const form = new FormData();
  form.append("image", file);
  try {
    const { data } = await axios.post<Prediction>(`${baseURL}/predict`, form, {
      timeout: 120_000,
      headers: { "Content-Type": "multipart/form-data" }
    });
    return data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail ?? error.response?.data;
      throw new Error(detail?.reason || "Analysis failed. Verify the inference service and try again.");
    }
    throw new Error("Analysis failed. Please try again.");
  }
}

