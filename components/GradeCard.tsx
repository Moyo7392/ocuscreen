import type { ScreeningResult } from "@/lib/types";
import { toneFor } from "@/lib/clinical";

const styles = { safe: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300", warning: "border-amber-500/30 bg-amber-500/10 text-amber-300", danger: "border-red-500/30 bg-red-500/10 text-red-300" };

export function GradeCard({ result }: { result: ScreeningResult }) {
  const tone = toneFor(result.grade);
  return <div className={`rounded-lg border border-l-2 p-6 ${styles[tone]}`}><p className="font-mono text-[9px] font-semibold uppercase tracking-[.2em] opacity-70">Predicted severity</p><div className="mt-4 flex items-end gap-5"><span className="font-mono text-[72px] font-medium leading-[.85] tracking-[-.08em]">{result.grade}</span><div className="pb-0.5"><p className="text-xs opacity-60">Grade {result.grade} of 4</p><p className="mt-1 text-[17px] font-medium text-slate-50">{result.grade_label}</p></div></div></div>;
}
