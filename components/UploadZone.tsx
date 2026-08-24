"use client";

import { useCallback, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import axios, { AxiosError } from "axios";
import { Check, FileImage, ScanLine, UploadCloud, X } from "lucide-react";

const MAX_SIZE = 10 * 1024 * 1024;
const TYPES = ["image/jpeg", "image/png"];

function validate(file: File) {
  if (!TYPES.includes(file.type)) return "Choose a JPEG or PNG fundus image.";
  if (file.size > MAX_SIZE) return "Image must be 10 MB or smaller.";
  return null;
}

export function UploadZone() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [processing, setProcessing] = useState(false);

  const choose = useCallback((next?: File) => {
    if (!next) return;
    const issue = validate(next);
    if (issue) { setError(issue); return; }
    if (preview) URL.revokeObjectURL(preview);
    setError(null); setFile(next); setPreview(URL.createObjectURL(next));
  }, [preview]);

  async function analyze() {
    if (!file) return;
    setProcessing(true); setError(null); setProgress(5);
    const data = new FormData(); data.append("image", file);
    try {
      const response = await axios.post("/api/inference", data, {
        headers: { Authorization: "Bearer demo-token" },
        onUploadProgress: ({ loaded, total }) => setProgress(Math.min(70, Math.round((loaded / (total || file.size)) * 70))),
      });
      setProgress(100);
      sessionStorage.setItem(`ocuscreen:result:${response.data.id}`, JSON.stringify(response.data));
      router.push(`/results/${response.data.id}`);
    } catch (caught) {
      const response = (caught as AxiosError<{ reason?: string }>).response;
      setError(response?.data?.reason || "The grading service is temporarily unavailable. Please try again.");
      setProcessing(false); setProgress(0);
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      {!file ? (
        <button type="button" onClick={() => inputRef.current?.click()} onDragEnter={(e) => { e.preventDefault(); setDragging(true); }} onDragOver={(e) => e.preventDefault()} onDragLeave={() => setDragging(false)} onDrop={(e) => { e.preventDefault(); setDragging(false); choose(e.dataTransfer.files[0]); }} className={`group flex min-h-[390px] w-full flex-col items-center justify-center rounded-xl border p-8 text-center transition duration-200 ${dragging ? "border-blue-400 bg-blue-500/[.06]" : "border-white/[.11] bg-[#0d131f] hover:border-slate-500"}`}>
          <span className="mb-7 grid h-14 w-14 place-items-center rounded-full border border-slate-600 text-slate-300 transition group-hover:border-blue-400 group-hover:text-blue-300"><UploadCloud size={23} strokeWidth={1.4} /></span>
          <span className="text-[18px] font-medium text-slate-100">Drop a fundus photograph</span>
          <span className="mt-2 text-[13px] text-slate-500">or select a file from this device</span>
          <span className="mt-8 font-mono text-[9px] uppercase tracking-[.16em] text-slate-700">JPEG / PNG · 10 MB maximum</span>
        </button>
      ) : (
        <div className="glass overflow-hidden rounded-xl">
          <div className="relative flex min-h-[390px] items-center justify-center bg-black/30 p-5">
            <img src={preview!} alt="Selected retinal fundus photograph" className="max-h-[410px] max-w-full rounded-xl object-contain" />
            {!processing && <button onClick={() => { setFile(null); setPreview(null); }} aria-label="Remove selected image" className="absolute right-4 top-4 grid h-11 w-11 place-items-center rounded-full bg-black/70 text-slate-300 hover:text-white"><X size={18}/></button>}
          </div>
          <div className="flex flex-col gap-5 border-t border-line p-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex min-w-0 items-center gap-3"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-emerald-500/10 text-emerald-400"><FileImage size={19}/></span><div className="min-w-0"><p className="truncate text-sm text-slate-200">{file.name}</p><p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB · Ready for analysis</p></div></div>
            <button disabled={processing} onClick={analyze} className="inline-flex min-h-12 min-w-44 items-center justify-center gap-2 rounded-md bg-slate-100 px-5 text-sm font-medium text-slate-950 transition hover:bg-white disabled:cursor-wait disabled:bg-slate-400">
              {processing ? <><span className="orbital h-5 w-5 rounded-full border border-white/20 border-t-white" /> Analyzing {progress}%</> : <><ScanLine size={18}/> Analyze image</>}
            </button>
          </div>
          {processing && <div className="h-1 bg-slate-800"><div className="h-full bg-blue-500 transition-all duration-300" style={{ width: `${progress}%` }} /></div>}
        </div>
      )}
      <input ref={inputRef} type="file" accept="image/jpeg,image/png" className="sr-only" onChange={(e) => choose(e.target.files?.[0])} />
      {error && <div role="alert" className="mt-5 flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200"><X className="mt-0.5 shrink-0" size={17}/>{error}</div>}
      <div className="mt-6 flex justify-center gap-2 text-xs text-slate-600"><Check size={15} className="text-emerald-500"/> Images are used only for this screening workflow. Do not upload patient-identifying data.</div>
    </div>
  );
}
