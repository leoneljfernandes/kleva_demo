import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // mismo origen que en Docker (nginx hace proxy de /api): sin CORS en desarrollo
    proxy: { "/api": process.env.VITE_API_TARGET ?? "http://localhost:8010" },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
  },
});
