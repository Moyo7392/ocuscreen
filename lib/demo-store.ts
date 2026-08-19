import type { ScreeningResult } from "./types";

const globalStore = globalThis as typeof globalThis & {
  ocuScreenResults?: Map<string, ScreeningResult & { user_id: string }>;
};

export const resultsStore =
  globalStore.ocuScreenResults ?? new Map<string, ScreeningResult & { user_id: string }>();

export const auditLog: ReadonlyArray<{ id: string; user_id: string; model_version: string; grade: number; timestamp: string }> = [];

export function appendAudit(entry: Omit<(typeof auditLog)[number], "id">) {
  // Deliberately expose no update/delete operation: audit events are append-only.
  (auditLog as Array<(typeof auditLog)[number]>).push({ id: crypto.randomUUID(), ...entry });
}

if (process.env.NODE_ENV !== "production") globalStore.ocuScreenResults = resultsStore;

export function demoUserId(request: Request) {
  const authorization = request.headers.get("authorization");
  if (authorization && !authorization.startsWith("Bearer ")) return null;
  return process.env.DEMO_USER_ID || "demo-clinician";
}
