export function OrbitalLoader() {
  return <div className="flex flex-col items-center gap-6 py-2 text-center" role="status" aria-live="polite">
    <span className="relative block h-16 w-16" aria-hidden="true">
      <span className="orbit absolute inset-0 rounded-full border border-white/[0.07]"><i className="absolute -top-1 left-1/2 h-2 w-2 -translate-x-1/2 rounded-full bg-accent shadow-[0_0_14px_rgba(79,140,255,.8)]"/></span>
      <span className="orbit-reverse absolute inset-[10px] rounded-full border border-white/[0.05]"><i className="absolute -bottom-1 left-1/2 h-2 w-2 -translate-x-1/2 rounded-full bg-[#8B8FF8]"/></span>
      <span className="absolute left-1/2 top-1/2 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/80"/>
    </span>
    <span><span className="block text-sm font-semibold tracking-clinical text-ink">Analyzing retinal image</span><span className="mt-2 block text-xs text-quiet">Quality · grading · attention map</span></span>
  </div>;
}
