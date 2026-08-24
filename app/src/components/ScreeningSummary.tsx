export function ScreeningSummary({ grade, confidence, recommendation, modelVersion }: { grade: number; confidence: number; recommendation: string; modelVersion: string }) {
  const referral = grade >= 2; const level = confidence > .8 ? "High" : confidence >= .5 ? "Moderate" : "Low";
  const levelTone = level === "High" ? "border-safe/20 bg-safe/[.08] text-safe" : level === "Moderate" ? "border-warning/20 bg-warning/[.08] text-warning" : "border-danger/20 bg-danger/[.08] text-danger";
  return <section className="instrument-card p-8 sm:p-10"><p className="section-kicker">Screening summary</p>
    <dl className="mt-7 divide-y divide-white/[0.06]">
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5"><dt className="text-xs text-quiet">Assessment</dt><dd className={`rounded-full border px-3 py-1.5 text-[11px] font-semibold ${referral ? "border-danger/20 bg-danger/[.08] text-danger" : "border-safe/20 bg-safe/[.08] text-safe"}`}>{referral ? "Referable Disease Detected" : "No Referable Disease"}</dd></div>
      <div className="py-5"><dt className="text-xs text-quiet">Action</dt><dd className="mt-2 text-sm font-semibold leading-6 text-ink">{recommendation}</dd></div>
      <div className="flex items-center justify-between gap-4 py-5"><dt className="text-xs text-quiet">Confidence level</dt><dd className={`rounded-full border px-3 py-1.5 text-[11px] font-semibold ${levelTone}`}>{level}</dd></div>
      <div className="flex flex-wrap justify-between gap-3 pt-5"><dt className="text-xs text-quiet">Model</dt><dd className="text-right font-mono text-[11px] leading-5 text-body">v{modelVersion}<br/>EfficientNet-B0 · APTOS 2019</dd></div>
    </dl>
  </section>;
}
