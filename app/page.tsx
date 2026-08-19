import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Brand } from "@/components/Brand";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col px-6">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between border-b border-white/[.07] py-6"><Brand /><span className="font-mono text-[10px] uppercase tracking-[.16em] text-slate-600">Retinauts / CSE 4316</span></div>
      <section className="mx-auto grid w-full max-w-6xl flex-1 items-center gap-20 py-20 lg:grid-cols-[1.15fr_.85fr]">
        <div>
          <p className="mb-7 font-mono text-[10px] uppercase tracking-[.22em] text-blue-400">Retinal screening support</p>
          <h1 className="max-w-3xl text-5xl font-medium leading-[1.06] tracking-[-.05em] text-white md:text-[68px]">A considered second look at the retina.</h1>
          <p className="mt-7 max-w-xl text-[17px] leading-8 text-slate-400">OcuScreen helps clinicians triage fundus photographs with a severity estimate, confidence signal, and a visual account of model attention.</p>
          <div className="mt-10 flex flex-wrap items-center gap-5"><Link href="/upload" className="inline-flex min-h-12 items-center gap-3 rounded-md bg-slate-100 px-5 text-sm font-medium text-slate-950 transition hover:bg-white">Enter demonstration <ArrowRight size={17} /></Link><span className="text-xs text-slate-600">No patient identifiers collected</span></div>
        </div>
        <div className="relative mx-auto aspect-square w-full max-w-[430px]">
          <div className="absolute inset-0 rounded-full border border-white/[.09]"/><div className="absolute inset-[12%] rounded-full border border-white/[.07]"/><div className="absolute inset-[25%] rounded-full border border-blue-400/20"/><div className="absolute inset-1/2 h-px w-[45%] origin-left bg-gradient-to-r from-blue-400/60 to-transparent"/>
          <div className="absolute left-1/2 top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border border-blue-300 bg-blue-500/20"/>
          <span className="absolute left-0 top-1/2 -translate-y-1/2 bg-ink py-2 pr-4 font-mono text-[9px] uppercase tracking-[.18em] text-slate-600">Acquisition</span>
          <span className="absolute bottom-[12%] right-0 bg-ink py-2 pl-4 font-mono text-[9px] uppercase tracking-[.18em] text-slate-600">Review / Refer</span>
        </div>
      </section>
      <div className="mx-auto grid w-full max-w-6xl grid-cols-1 border-t border-white/[.07] py-5 text-[11px] text-slate-600 sm:grid-cols-3"><span>Quality-controlled input</span><span className="sm:text-center">Five-level severity scale</span><span className="sm:text-right">Decision support only</span></div>
    </main>
  );
}
