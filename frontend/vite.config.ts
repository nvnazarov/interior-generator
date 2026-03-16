import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: process.env.FRONTEND__API__HOST,
    port:
      (process.env.FRONTEND__API__PORT &&
        Number(process.env.FRONTEND__API__PORT)) ||
      undefined,
    allowedHosts: ["frontend"],
  },
  envPrefix: "FRONTEND__",
  base: process.env.FRONTEND__PROXY__BASE_PATH,
});
