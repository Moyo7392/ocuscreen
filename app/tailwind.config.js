/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: { extend: {
    colors: { ivory:"#FAFAF7", surface:"#FFFFFF", taupe:"#E8E4DF", teal:"#1B4D6E", sea:"#2E8B83", safe:"#3A8F6E", warning:"#D4913B", danger:"#C4454D", ink:"#1A1A1A", body:"#6B7280", quiet:"#9CA3AF", wash:"#F0F7FA", gold:"#B8963E", notice:"#F0EEEB" },
    fontFamily: { sans:["Inter","ui-sans-serif","system-ui"], serif:["DM Serif Display","Georgia","serif"], mono:["JetBrains Mono","ui-monospace","monospace"] },
    boxShadow: { clinical:"0 14px 40px rgba(43,37,31,.07)", float:"0 20px 55px rgba(43,37,31,.1)" }
  } }, plugins: []
};
