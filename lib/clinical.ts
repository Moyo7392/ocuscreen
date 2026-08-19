import type { Grade } from "./types";

export const GRADE_LABELS: Record<Grade, string> = {
  0: "No apparent DR",
  1: "Mild NPDR",
  2: "Moderate NPDR",
  3: "Severe NPDR",
  4: "Proliferative DR",
};

export const DISCLAIMER =
  "OcuScreen is a decision-support and triage aid. It is not an FDA-cleared diagnostic device and does not replace examination by a licensed clinician.";

export const recommendationFor = (grade: Grade) =>
  grade <= 1
    ? "Routine rescreening recommended."
    : "Referral to an ophthalmologist is advised.";

export const toneFor = (grade: Grade) =>
  grade <= 1 ? "safe" : grade === 2 ? "warning" : "danger";
