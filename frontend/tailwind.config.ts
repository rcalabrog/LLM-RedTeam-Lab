import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0b1220",
        panel: "#111a2e",
        accent: "#4fd1c5",
        accentSoft: "#2dd4bf"
      }
    }
  },
  plugins: []
};

export default config;
