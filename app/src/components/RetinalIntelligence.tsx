import type {StoredScreening} from "@/services/types";

const population = [1805, 370, 999, 193, 295];
const followUp = [
  {risk:"Low", window:"Routine rescreen in 12 months", detail:"No diabetic retinopathy was detected in this screening image."},
  {risk:"Mild", window:"Clinical review; rescreen in 6–12 months", detail:"Early changes deserve monitoring for progression."},
  {risk:"Moderate", window:"Refer for assessment within 4–6 weeks", detail:"Referable diabetic retinopathy may require closer surveillance or treatment."},
  {risk:"High", window:"Urgent ophthalmology review within 1–2 weeks", detail:"Severe changes can precede vision-threatening complications."},
  {risk:"Critical", window:"Urgent specialist review within 24–48 hours", detail:"Proliferative changes require prompt clinical assessment."},
];

export function RetinalIntelligence({result}:{result:StoredScreening}) {
  const plan=followUp[Math.max(0,Math.min(4,result.grade))];
  return <div className="grid gap-7 xl:grid-cols-3">
    <DecisionPath result={result} plan={plan}/>
    <QuadrantDensity result={result}/>
    <PopulationContext grade={result.grade}/>
  </div>;
}

function DecisionPath({result,plan}:{result:StoredScreening;plan:(typeof followUp)[number]}) {
  const confidence=Math.round(result.confidence*100);
  const nodes=[
    ["Image quality",result.quality_check??"Passed"],
    ["AI screening",`Grade ${result.grade} · ${result.grade_label}`],
    ["Confidence",`${confidence}% · ${confidence>=85?"High":confidence>=65?"Moderate":"Review advised"}`],
    ["Clinical pathway",plan.window],
  ];
  return <section className="clinical-card p-7 xl:col-span-2" aria-labelledby="decision-path-title">
    <p className="report-label">Clinical decision pathway</p>
    <h3 id="decision-path-title" className="mt-3 font-serif text-2xl text-ink">From scan to next step</h3>
    <div className="mt-7 grid gap-3 sm:grid-cols-4">{nodes.map(([label,value],index)=><div key={label} className="relative rounded-2xl border border-taupe bg-[#FCFBF9] p-4">
      <span className="font-mono text-[10px] text-gold">0{index+1}</span>
      <p className="mt-2 text-[11px] font-semibold uppercase tracking-[.12em] text-quiet">{label}</p>
      <p className="mt-2 text-sm font-medium leading-5 text-ink">{value}</p>
      {index<nodes.length-1&&<span aria-hidden className="absolute -right-3 top-1/2 z-10 hidden text-gold sm:block">→</span>}
    </div>)}</div>
    <div className="mt-5 rounded-2xl bg-wash p-5"><p className="text-sm font-semibold text-teal">{plan.risk} progression concern</p><p className="mt-1 text-sm leading-6 text-body">{plan.detail} This pathway supports—not replaces—a dilated examination and clinician judgment.</p></div>
  </section>;
}

function QuadrantDensity({result}:{result:StoredScreening}) {
  const labels=["Superior temporal","Superior nasal","Inferior temporal","Inferior nasal"];
  const counts=[0,0,0,0];
  for(const spot of result.hotspots??[]) {
    const superior=spot.y<0.5, temporal=spot.x<0.5;
    counts[superior?(temporal?0:1):(temporal?2:3)]++;
  }
  return <section className="clinical-card p-7" aria-labelledby="quadrants-title"><p className="report-label">Lesion distribution</p><h3 id="quadrants-title" className="mt-3 font-serif text-2xl text-ink">Retinal quadrants</h3><div className="mt-6 grid grid-cols-2 overflow-hidden rounded-2xl border border-taupe">{counts.map((count,index)=><div key={labels[index]} className="min-h-28 border-b border-r border-taupe p-4 last:border-b-0"><p className="text-[10px] font-semibold uppercase tracking-wider text-quiet">{labels[index]}</p><p className="mt-3 font-mono text-2xl text-ink">{count}</p><p className={`mt-1 text-xs ${count>=3?"text-alert":count?"text-gold":"text-safe"}`}>{count>=3?"High density":count?"Attention":"No hotspot"}</p></div>)}</div><p className="mt-4 text-xs leading-5 text-quiet">Counts represent model-attention regions, not confirmed clinical lesions.</p></section>;
}

function PopulationContext({grade}:{grade:number}) {
  const total=population.reduce((sum,value)=>sum+value,0), count=population[grade]??0;
  const percent=Math.round(count/total*100);
  return <section className="clinical-card p-7 xl:col-span-3" aria-labelledby="population-title"><div className="grid items-center gap-7 md:grid-cols-[1fr_1.5fr]"><div><p className="report-label">APTOS population context</p><h3 id="population-title" className="mt-3 font-serif text-2xl text-ink">About {percent} in 100 training cases were Grade {grade}</h3><p className="mt-3 text-sm leading-6 text-body">This reference describes the 3,662-image APTOS training dataset—not disease prevalence in the general population.</p></div><div><div className="flex h-5 overflow-hidden rounded-full bg-wash" aria-label="APTOS class distribution">{population.map((value,index)=><span key={index} title={`Grade ${index}: ${value}`} className={`${index===grade?"bg-gold":"bg-teal/20"} transition-colors`} style={{width:`${value/total*100}%`}}/>)}</div><div className="mt-4 flex flex-wrap gap-x-5 gap-y-2">{population.map((value,index)=><span key={index} className={`text-xs ${index===grade?"font-semibold text-ink":"text-quiet"}`}><i className={`mr-2 inline-block h-2 w-2 rounded-full ${index===grade?"bg-gold":"bg-teal/20"}`}/>Grade {index}: {Math.round(value/total*100)}%</span>)}</div></div></div></section>;
}
