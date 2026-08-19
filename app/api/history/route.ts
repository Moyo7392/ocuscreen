import { NextResponse } from "next/server";
import { demoUserId, resultsStore } from "@/lib/demo-store";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const userId = demoUserId(request);
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  const { searchParams } = new URL(request.url);
  const page = Math.max(1, Number(searchParams.get("page")) || 1);
  const limit = Math.min(50, Math.max(1, Number(searchParams.get("limit")) || 20));
  const owned = [...resultsStore.values()].filter((item) => item.user_id === userId).sort((a, b) => b.timestamp.localeCompare(a.timestamp));
  return NextResponse.json({ items: owned.slice((page - 1) * limit, page * limit), page, limit, total: owned.length });
}
