import { Navbar } from "@/components/Navbar";
import { UploadZone } from "@/components/UploadZone";

export default function UploadPage() {
  return <><Navbar /><main className="min-h-[calc(100vh-4.5rem)] px-5 py-12"><div className="mx-auto w-full max-w-6xl"><div className="mb-10 grid gap-5 border-b border-white/[.07] pb-9 md:grid-cols-[1fr_auto] md:items-end"><div><p className="mb-3 font-mono text-[10px] uppercase tracking-[.22em] text-blue-400">New screening / 01</p><h1 className="text-3xl font-medium tracking-[-.035em] md:text-[42px]">Submit a fundus photograph</h1><p className="mt-3 max-w-2xl text-[15px] leading-7 text-slate-500">The image is validated before it is sent for grading. Do not include names, labels, or other patient-identifying information.</p></div><div className="border-l border-amber-400/50 pl-4 text-xs leading-5 text-slate-500"><strong className="block font-medium text-amber-300">Demonstration mode</strong>Results are simulated until a trained model is connected.</div></div><UploadZone /></div></main></>;
}
