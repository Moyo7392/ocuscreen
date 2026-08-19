"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { History, LogOut, ScanEye } from "lucide-react";
import { Brand } from "./Brand";

const links = [
  { href: "/upload", label: "New screening", icon: ScanEye },
  { href: "/history", label: "History", icon: History },
];

export function Navbar() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-30 border-b border-white/[.07] bg-ink/95 backdrop-blur-md">
      <div className="mx-auto flex h-[72px] max-w-[1440px] items-center justify-between px-5 lg:px-10">
        <Link href="/upload" aria-label="OcuScreen home"><Brand /></Link>
        <nav aria-label="Primary navigation" className="flex items-center gap-1">
          {links.map(({ href, label, icon: Icon }) => {
            const active = pathname.startsWith(href);
            return (
              <Link key={href} href={href} className={`relative flex min-h-11 items-center gap-2 px-3 text-[13px] transition ${active ? "text-white" : "text-slate-500 hover:text-slate-200"}`}>
                <Icon size={17} aria-hidden="true" /><span className="hidden sm:inline">{label}</span>
                {active && <span className="absolute inset-x-3 -bottom-[14px] h-px bg-blue-400" />}
              </Link>
            );
          })}
          <span className="mx-3 hidden h-6 w-px bg-line md:block" />
          <div className="hidden text-right md:block"><p className="text-xs text-slate-300">Demo Clinician</p><p className="text-[10px] text-slate-600">demo@ocuscreen.com</p></div>
          <Link href="/" aria-label="Sign out" className="ml-2 grid min-h-11 min-w-11 place-items-center rounded-lg text-slate-500 transition hover:bg-white/5 hover:text-slate-200"><LogOut size={17} /></Link>
        </nav>
      </div>
    </header>
  );
}
