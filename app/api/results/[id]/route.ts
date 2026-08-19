import { NextResponse } from "next/server";
import { demoUserId, resultsStore } from "@/lib/demo-store";

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const userId = demoUserId(request);
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  const result = resultsStore.get((await params).id);
  if (!result) return NextResponse.json({ error: "not_found" }, { status: 404 });
  if (result.user_id !== userId) return NextResponse.json({ error: "forbidden" }, { status: 403 });
  return NextResponse.json(result);
}
