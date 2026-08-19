export function ConfidenceRing({ value }: { value: number }) {
  const percent = Math.round(value * 100);
  return (
    <div className="flex items-center gap-5">
      <div role="img" aria-label={`Model confidence ${percent} percent`} className="relative grid h-24 w-24 shrink-0 place-items-center rounded-full" style={{ background: `conic-gradient(#3b82f6 ${percent * 3.6}deg, #1e293b 0deg)` }}>
        <div className="grid h-[78px] w-[78px] place-items-center rounded-full bg-surface"><span className="font-mono text-xl font-semibold">{percent}%</span></div>
      </div>
      <div><p className="font-medium text-slate-100">Model Confidence</p><p className="mt-1 text-sm leading-6 text-slate-500">Confidence in the selected severity class—not a probability of correctness.</p></div>
    </div>
  );
}
