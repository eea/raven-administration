import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";
import Icons from "unplugin-icons/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), Icons(), tailwindcss()],
  server: {
    proxy: {
      "/api": {
        // 127.0.0.1, not localhost: the dev API binds IPv4 only, while a stray
        // published container port can own ::1:5000 and silently shadow it.
        // RAVEN_API_URL lets a second checkout run against its own API port.
        target: process.env.RAVEN_API_URL || "http://127.0.0.1:5000",
        changeOrigin: true,
        secure: false,
        ws: true
      }
    }
  }
});
