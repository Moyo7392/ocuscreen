"use client";
import {useEffect,useState} from "react"; import {useRouter} from "next/navigation"; import {Navbar} from "./Navbar"; import {storage} from "@/services/storage";
export function AppShell({children}:{children:React.ReactNode}){ const router=useRouter(); const [ready,setReady]=useState(false); useEffect(()=>{if(!storage.signedIn())router.replace("/");else setReady(true)},[router]); if(!ready)return <div className="min-h-screen bg-ivory"/>; return <><Navbar/><main className="page-in mx-auto min-h-[calc(100vh-56px)] max-w-[1320px] px-5 py-10 sm:px-8 sm:py-14">{children}</main></>; }
