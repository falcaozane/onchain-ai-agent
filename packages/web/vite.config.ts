import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig, loadEnv } from "vite";

export default defineConfig({
  define: {
    "process.env": loadEnv("", process.cwd()),
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})

