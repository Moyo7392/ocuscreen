"use client";

import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

export function HeatmapOverlay({ imageUrl, heatmapUrl }: { imageUrl: string; heatmapUrl: string }) {
  const [visible, setVisible] = useState(true);
  return (
    <div>
      <div className="relative flex min-h-[430px] items-center justify-center overflow-hidden rounded-xl bg-black/35">
        <img src={visible ? heatmapUrl : imageUrl} alt={visible ? "Retinal image with model-attention heatmap overlay" : "Submitted retinal image without heatmap"} className="max-h-[650px] w-full object-contain" />
        <span className="absolute left-4 top-4 rounded-md border border-white/10 bg-black/60 px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-slate-300">{visible ? "Grad-CAM overlay" : "Original image"}</span>
      </div>
      <button type="button" aria-pressed={visible} onClick={() => setVisible((value) => !value)} className="mt-4 inline-flex min-h-11 items-center gap-2 rounded-lg border border-line bg-white/[.025] px-4 text-sm text-slate-300 transition hover:bg-white/5 hover:text-white">{visible ? <EyeOff size={17}/> : <Eye size={17}/>} {visible ? "Hide overlay" : "Show overlay"}</button>
    </div>
  );
}
