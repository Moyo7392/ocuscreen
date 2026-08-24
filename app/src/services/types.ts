export interface Prediction {
  grade: number;
  grade_label: string;
  confidence: number;
  model_version: string;
  heatmap_base64: string;
  recommendation: string;
  probabilities: Record<"0" | "1" | "2" | "3" | "4", number>;
  hotspots: Hotspot[];
  image_metadata: { width: number; height: number; file_size_bytes: number };
  processing_time_ms: number;
  quality_check: "Passed";
}

export interface Hotspot {
  id: number;
  x: number;
  y: number;
  area: number;
  activation: number;
  anatomy: string;
  description: string;
}

export interface StoredScreening extends Prediction {
  id: string;
  timestamp: string;
  image_data_url: string;
  file_name?: string;
}
