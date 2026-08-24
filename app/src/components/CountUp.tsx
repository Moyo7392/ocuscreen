"use client";
import { useEffect,useRef,useState } from "react";
export function CountUp({ value, duration=800, suffix="" }: { value:number; duration?:number; suffix?:string }) {
  const [display,setDisplay]=useState(0); const frame=useRef<number|null>(null);
  useEffect(()=>{ const start=performance.now(); const tick=(now:number)=>{ const progress=Math.min((now-start)/duration,1); setDisplay(Math.round(value*(1-Math.pow(1-progress,3)))); if(progress<1)frame.current=requestAnimationFrame(tick); }; frame.current=requestAnimationFrame(tick); return()=>{if(frame.current)cancelAnimationFrame(frame.current)}; },[value,duration]);
  return <>{display}{suffix}</>;
}
