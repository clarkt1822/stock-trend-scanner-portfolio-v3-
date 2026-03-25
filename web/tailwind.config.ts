import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#07111f",
        foreground: "#e6eef8",
        card: "#0d1829",
        border: "#1c3047",
        muted: "#8aa0bd",
        accent: "#5eead4",
        positive: "#34d399",
        warning: "#f59e0b",
      },
      boxShadow: {
        glow: "0 20px 60px rgba(6, 182, 212, 0.18)",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "ui-sans-serif", "system-ui"],
        mono: ["var(--font-geist-mono)", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
