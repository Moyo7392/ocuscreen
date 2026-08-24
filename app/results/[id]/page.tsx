import { Navbar } from "@/components/Navbar";
import { ResultLoader } from "@/components/ResultLoader";

export default async function ResultPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <><Navbar/><ResultLoader id={id}/></>;
}
