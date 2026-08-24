"use client";
import { useState } from "react";
import type { Hotspot } from "@/services/types";

type ViewMode = "original" | "overlay" | "compare";
export function HeatmapOverlay({ original, heatmap, hotspots, severityColor, width, height }: { original: string; heatmap: string; hotspots: Hotspot[]; severityColor: string; width: number; height: number }) {
  const [mode, setMode] = useState<ViewMode>("overlay");
  return <section className="instrument-card overflow-hidden">
    <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/[0.06] px-5 py-4 sm:px-6"><div><p className="section-kicker">Retinal capture</p></div><div className="flex rounded-full border border-white/[0.08] bg-canvas/70 p-1" role="group" aria-label="Image view">
      {(["original", "overlay", "compare"] as ViewMode[]).map(value => <button key={value} onClick={() => setMode(value)} aria-pressed={mode === value} className={`min-h-9 rounded-full px-4 text-[11px] font-semibold capitalize transition duration-200 ${mode === value ? "bg-white/[0.09] text-ink" : "text-quiet hover:text-body"}`}>{value === "compare" ? "Side by side" : value}</button>)}
    </div></div>
    <div className={`${mode === "compare" ? "grid md:grid-cols-2" : "block"} bg-black`}>
      {(mode === "original" || mode === "compare") && <ImagePanel src={original} alt="Original retinal fundus photograph" label="Original" width={width} height={height}/>} 
      {(mode === "overlay" || mode === "compare") && <ImagePanel src={heatmap} alt="Grad-CAM attention heatmap overlay" label="Grad-CAM overlay" hotspots={hotspots} width={width} height={height}/>} 
    </div>
    <div className="border-t border-white/[0.06] p-6 sm:p-8" style={{borderLeft:`4px solid ${severityColor}`}}><p className="section-kicker">Findings</p>
      {hotspots.length ? <ol className="mt-5 space-y-4">{hotspots.map(region => <li key={region.id} className="flex gap-4 text-sm leading-6"><span className="font-mono text-accent">{region.id.toString().padStart(2,"0")}</span><span className="text-body"><strong className="font-semibold text-ink">Region {region.id}</strong> — {region.description} ({region.anatomy})</span></li>)}</ol> : <p className="mt-4 text-sm text-body">No discrete high-activation region exceeded the reporting threshold.</p>}
      <p className="mt-5 text-[11px] leading-5 text-quiet">Locations are image-relative attention regions, not lesion detections. Nasal and temporal orientation depends on eye laterality.</p>
    </div>
  </section>;
}

function ImagePanel({ src, alt, label, hotspots = [], width, height }: { src: string; alt: string; label: string; hotspots?: Hotspot[]; width: number; height: number }) {
  return <div className="relative flex w-full items-center justify-center overflow-hidden bg-black" style={{aspectRatio: `${width || 1} / ${height || 1}`}}>
    {/* eslint-disable-next-line @next/next/no-img-element */}<img src={src} alt={alt} className="block h-full w-full object-contain"/>
    {hotspots.map((region, index) => <span key={region.id} className="hotspot-marker pointer-events-none absolute grid h-10 w-10 place-items-center rounded-full border border-white/80 bg-black/35 font-mono text-xs font-semibold text-white shadow-[0_0_0_7px_rgba(255,255,255,.08)] backdrop-blur-sm" style={{left:`${region.x * 100}%`, top:`${region.y * 100}%`, animationDelay:`${index * 110 + 250}ms`}}><i className="absolute left-1/2 top-[-8px] h-[56px] w-px -translate-x-1/2 bg-white/25"/><i className="absolute left-[-8px] top-1/2 h-px w-[56px] -translate-y-1/2 bg-white/25"/><b className="relative not-italic">{region.id}</b></span>)}
    <span className="absolute bottom-5 left-5 rounded-full border border-white/[0.08] bg-[#080C13]/70 px-4 py-2 text-[11px] text-white/60 backdrop-blur-xl">{label}</span>
  </div>;
}
