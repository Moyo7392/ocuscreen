"use client";
import { useEffect, useRef } from "react";
export function ScrollReveal({ children, className="", direction="up", delay=0 }: { children:React.ReactNode; className?:string; direction?:"up"|"left"|"right"; delay?:number }) {
  const ref=useRef<HTMLDivElement>(null);
  useEffect(()=>{ const node=ref.current; if(!node)return; const observer=new IntersectionObserver(([entry])=>{ if(entry.isIntersecting){ node.classList.add("animate-in"); observer.unobserve(node); } },{threshold:.15}); observer.observe(node); return()=>observer.disconnect(); },[]);
  const motion=direction==="left"?"reveal-left":direction==="right"?"reveal-right":"reveal";
  return <div ref={ref} className={`${motion} ${className}`} style={{transitionDelay:`${delay}ms`}}>{children}</div>;
}
