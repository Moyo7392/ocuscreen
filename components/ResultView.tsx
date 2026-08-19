import Link from "next/link";
import { AlertTriangle, ArrowLeft, Download, Stethoscope } from "lucide-react";
import type { ScreeningResult } from "@/lib/types";
import { ConfidenceRing } from "./ConfidenceRing";
import { Disclaimer } from "./Disclaimer";
import { GradeCard } from "./GradeCard";
import { HeatmapOverlay } from "./HeatmapOverlay";

export function ResultView({ result }: { result: ScreeningResult }) {
  const threshold = Number(process.env.LOW_CONFIDENCE_THRESHOLD || .7);
  const low = result.confidence < threshold;
  return (
    <main className="mx-auto max-w-[1440px] px-5 py-9 lg:px-10">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4"><Link href="/upload" className="inline-flex min-h-11 items-center gap-2 text-sm text-slate-400 hover:text-white"><ArrowLeft size={17}/> New screening</Link><a href={`/api/export/${result.id}`} className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-line bg-surface px-4 text-sm text-slate-200 hover:border-slate-600"><Download size={17}/> Export PDF</a></div>
      {low && <div role="alert" className="mb-6 flex gap-3 rounded-xl border border-red-500/50 bg-red-500/10 p-4 text-red-100"><AlertTriangle className="shrink-0 text-red-400"/><div><p className="font-semibold">Low confidence — human review required before acting on this result</p><p className="mt-1 text-sm text-red-200/70">The model confidence is below the calibrated review threshold of {Math.round(threshold * 100)}%.</p></div></div>}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,3fr)_minmax(330px,2fr)]">
        <section aria-label="Retinal image visualization" className="glass rounded-xl p-4"><HeatmapOverlay imageUrl={result.image_url} heatmapUrl={result.heatmap_url}/></section>
        <section aria-label="Screening result" className="space-y-5"><GradeCard result={result}/><div className="glass rounded-xl p-6"><ConfidenceRing value={result.confidence}/></div><div className="glass rounded-xl border-l-2 border-l-amber-500 p-6"><div className="flex gap-3"><Stethoscope className="mt-0.5 shrink-0 text-amber-400" size={21}/><div><p className="text-xs font-semibold uppercase tracking-[.16em] text-slate-500">Advisory recommendation</p><p className="mt-2 leading-7 text-slate-100">{result.recommendation}</p></div></div></div><div className="flex justify-between px-1 font-mono text-[11px] text-slate-600"><span>MODEL {result.model_version}</span><time dateTime={result.timestamp}>{new Date(result.timestamp).toLocaleString()}</time></div></section>
      </div>
      <div className="mt-6"><Disclaimer/></div>
    </main>
  );
}
