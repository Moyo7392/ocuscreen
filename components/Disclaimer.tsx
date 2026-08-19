import { ShieldCheck } from "lucide-react";
import { DISCLAIMER } from "@/lib/clinical";

export function Disclaimer() {
  return (
    <aside aria-label="Medical disclaimer" className="flex gap-3 rounded-xl border border-slate-700 bg-slate-800/70 p-4 text-sm leading-6 text-slate-300">
      <ShieldCheck className="mt-0.5 shrink-0 text-blue-400" size={19} aria-hidden="true" />
      <p><strong className="font-semibold text-slate-100">Clinical notice.</strong> {DISCLAIMER}</p>
    </aside>
  );
}
