import React from "react";
import { Document, Image, Page, StyleSheet, Text, View, renderToBuffer } from "@react-pdf/renderer";
import { demoUserId, resultsStore } from "@/lib/demo-store";
import { DISCLAIMER } from "@/lib/clinical";

export const runtime = "nodejs";
const styles = StyleSheet.create({ page: { padding: 36, backgroundColor: "#0A0E17", color: "#F1F5F9", fontFamily: "Helvetica" }, brand: { fontSize: 18, marginBottom: 4 }, muted: { color: "#94A3B8", fontSize: 9 }, row: { flexDirection: "row", gap: 14, marginTop: 24 }, image: { width: 252, height: 252, objectFit: "contain", backgroundColor: "#05070b" }, card: { flex: 1, padding: 18, backgroundColor: "#141B2D", borderRadius: 8 }, grade: { fontSize: 46, marginVertical: 8 }, label: { fontSize: 16, marginBottom: 20 }, item: { fontSize: 10, marginBottom: 10 }, disclaimer: { marginTop: 24, padding: 14, backgroundColor: "#1E293B", borderRadius: 6, fontSize: 9, lineHeight: 1.5 } });

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const userId = demoUserId(request);
  if (!userId) return new Response("Unauthorized", { status: 401 });
  const result = resultsStore.get((await params).id) as (ReturnType<typeof resultsStore.get> & { image_data?: string; heatmap_data?: string });
  if (!result) return new Response("Not found", { status: 404 });
  if (result.user_id !== userId) return new Response("Forbidden", { status: 403 });
  const e = React.createElement;
  const doc = e(Document, {}, e(Page, { size: "A4", style: styles.page },
    e(Text, { style: styles.brand }, "OcuScreen — Screening Result"), e(Text, { style: styles.muted }, "AI-assisted diabetic retinopathy decision support"),
    e(View, { style: styles.row }, e(View, {}, e(Image, { style: styles.image, src: result.image_data }), e(Text, { style: [styles.muted, { marginTop: 5 }] }, "Submitted image")), e(View, {}, e(Image, { style: styles.image, src: result.heatmap_data }), e(Text, { style: [styles.muted, { marginTop: 5 }] }, "Grad-CAM attention overlay"))),
    e(View, { style: styles.card }, e(Text, { style: styles.muted }, "PREDICTED SEVERITY"), e(Text, { style: styles.grade }, `GRADE ${result.grade}`), e(Text, { style: styles.label }, result.grade_label), e(Text, { style: styles.item }, `Model Confidence: ${Math.round(result.confidence * 100)}%`), e(Text, { style: styles.item }, `Recommendation: ${result.recommendation}`), e(Text, { style: styles.item }, `Model version: ${result.model_version}`), e(Text, { style: styles.item }, `Timestamp: ${new Date(result.timestamp).toISOString()}`)),
    e(Text, { style: styles.disclaimer }, DISCLAIMER)
  ));
  const buffer = await renderToBuffer(doc);
  return new Response(new Uint8Array(buffer), { headers: { "Content-Type": "application/pdf", "Content-Disposition": `attachment; filename="ocuscreen-${result.id}.pdf"` } });
}
