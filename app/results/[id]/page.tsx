import { notFound } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { ResultView } from "@/components/ResultView";
import { resultsStore } from "@/lib/demo-store";

export const dynamic = "force-dynamic";

export default async function ResultPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = resultsStore.get(id);
  if (!result) notFound();
  return <><Navbar/><ResultView result={result}/></>;
}
