export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3.5">
      <span className="relative grid h-9 w-9 place-items-center rounded-full border border-slate-500/50" aria-hidden="true">
        <span className="h-3.5 w-3.5 rounded-full border border-blue-400 bg-blue-500/20" />
        <span className="absolute h-px w-5 bg-slate-500/70" />
      </span>
      {!compact && <span className="text-[17px] font-semibold tracking-[-.025em]">OcuScreen</span>}
    </div>
  );
}
