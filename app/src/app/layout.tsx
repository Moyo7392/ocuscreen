import type { Metadata } from "next";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/jetbrains-mono/600.css";
import "@fontsource/dm-serif-display/400.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "OcuScreen | Retinal screening support",
  description: "AI-assisted diabetic retinopathy screening support by Retinauts."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
