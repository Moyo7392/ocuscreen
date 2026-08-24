import type { StoredScreening } from "@/services/types";

const findings = [
  "No model-detected diabetic-retinopathy features were dominant in this image.",
  "Subtle findings may be present; image quality and model uncertainty can affect this result.",
  "Model attention is consistent with findings that warrant clinical review.",
  "Pronounced findings were detected; prompt specialist review is recommended.",
  "Advanced findings were detected; urgent specialist review is recommended.",
];

export function HealthyComparison({ result }: { result: StoredScreening }) {
  return (
    <section>
      <p className="report-label">Result context</p>
      <h2 className="serif-title mt-2 text-3xl">Understand the model output</h2>
      <div className="clinical-card mt-6 border-l-4 border-l-gold p-6 sm:p-8">
        <p className="text-sm leading-7 text-body">{findings[result.grade]}</p>
        <p className="mt-3 text-xs leading-5 text-quiet">
          OcuScreen does not compare this upload with a matched healthy control. Differences in
          camera, lighting, field of view, and image quality can affect both predictions and the
          attention overlay. A licensed clinician must interpret the original image.
        </p>
      </div>
    </section>
  );
}
