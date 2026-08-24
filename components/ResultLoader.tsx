"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ResultView } from "@/components/ResultView";
import type { ScreeningResult } from "@/lib/types";

export function ResultLoader({ id }: { id: string }) {
  const [result, setResult] = useState<ScreeningResult | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      try {
        const response = await fetch(`/api/results/${id}`, {
          headers: { Authorization: "Bearer demo-token" },
          signal: controller.signal,
        });
        if (response.ok) {
          setResult(await response.json());
          return;
        }
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") return;
      }

      const stored = sessionStorage.getItem(`ocuscreen:result:${id}`);
      if (stored) {
        try {
          setResult(JSON.parse(stored) as ScreeningResult);
          return;
        } catch {
          sessionStorage.removeItem(`ocuscreen:result:${id}`);
        }
      }
      setMissing(true);
    }

    void load();
    return () => controller.abort();
  }, [id]);

  if (result) return <ResultView result={result} />;

  return (
    <main className="mx-auto flex min-h-[calc(100vh-4.5rem)] max-w-3xl items-center px-6 py-16">
      <div className="w-full rounded-xl border border-white/[.09] bg-[#0d131f] p-8 text-center">
        {missing ? (
          <>
            <h1 className="text-2xl font-medium text-white">Screening result unavailable</h1>
            <p className="mt-3 text-sm leading-6 text-slate-400">
              Demo results last only for the current browser session. Submit the image again to create a new result.
            </p>
            <Link className="mt-6 inline-flex min-h-11 items-center rounded-md bg-slate-100 px-5 text-sm font-medium text-slate-950" href="/upload">
              Start a new screening
            </Link>
          </>
        ) : (
          <p className="font-mono text-xs uppercase tracking-[.18em] text-slate-500">Loading result…</p>
        )}
      </div>
    </main>
  );
}
