export function ConfidenceRing({ confidence }: { confidence: number }) {
  const percent = Math.round(confidence * 100); const radius = 48; const circumference = 2 * Math.PI * radius;
  return <section className="instrument-card flex items-center gap-8 p-8 sm:p-10">
    <div className="relative h-32 w-32 shrink-0">
      <svg className="h-full w-full -rotate-90" viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r={radius} fill="none" stroke="rgba(255,255,255,.055)" strokeWidth="7"/><circle className="confidence-ring" cx="60" cy="60" r={radius} fill="none" stroke="#4F8CFF" strokeWidth="7" strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={circumference * (1 - confidence)} style={{filter:"drop-shadow(0 0 6px rgba(79,140,255,.4))"}}/></svg>
      <span className="absolute inset-0 grid place-items-center font-mono text-2xl font-semibold tracking-[-.05em] text-ink">{percent}%</span>
    </div>
    <div><p className="section-kicker">Confidence</p><p className="mt-3 text-sm leading-6 text-body">Strength of the model signal for the selected grade.</p></div>
  </section>;
}
