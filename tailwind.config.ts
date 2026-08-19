import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0A0E17",
        surface: "#141B2D",
        line: "#1E293B",
        clinical: "#3B82F6",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "Inter", "sans-serif"],
        mono: ["var(--font-jetbrains)", "JetBrains Mono", "monospace"],
      },
      boxShadow: { instrument: "0 24px 70px rgba(0, 0, 0, .32)" },
    },
  },
  plugins: [],
} satisfies Config;
