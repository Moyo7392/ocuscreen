const styles = {
  safe: { color: "#24C98A", glow: "0 0 34px rgba(36,201,138,.22)" },
  warning: { color: "#F2AD3D", glow: "0 0 34px rgba(242,173,61,.22)" },
  danger: { color: "#F05D67", glow: "0 0 34px rgba(240,93,103,.22)" }
};
export function GradeCard({ grade, label }: { grade: number; label: string }) {
  const severity = grade <= 1 ? "safe" : grade === 2 ? "warning" : "danger";
  const tone = styles[severity];
  return <section className="instrument-card relative overflow-hidden p-8 sm:p-10" style={{ borderLeft: `4px solid ${tone.color}` }}>
    <p className="section-kicker">Severity grade</p>
    <div className="mt-5 flex items-end gap-6"><strong className="font-mono text-[72px] font-bold leading-[.82] tracking-[-.07em]" style={{ color: tone.color, textShadow: tone.glow }}>{grade}</strong><span className="pb-1 text-xl font-semibold tracking-clinical text-ink sm:text-2xl">{label}</span></div>
    <p className="mt-7 text-xs text-quiet">International Clinical DR scale · Grade 0–4</p>
  </section>;
}
