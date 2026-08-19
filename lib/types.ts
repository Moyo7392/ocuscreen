export type Grade = 0 | 1 | 2 | 3 | 4;

export interface ScreeningResult {
  id: string;
  grade: Grade;
  grade_label: string;
  confidence: number;
  model_version: string;
  image_url: string;
  heatmap_url: string;
  recommendation: string;
  timestamp: string;
}

export interface HistoryResponse {
  items: ScreeningResult[];
  page: number;
  limit: number;
  total: number;
}
