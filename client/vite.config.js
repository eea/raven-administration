import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from "unplugin-vue-components/vite"
import AutoImport from "unplugin-auto-import/vite"
import { VitePluginFonts } from 'vite-plugin-fonts'
import Icons from 'unplugin-icons/vite'

// https://vitejs.dev/config/
export default defineConfig({
  server:
  {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  plugins: [
    vue(),
    Icons(),
    Components(),
    AutoImport({
      imports: [
        'vue'
      ]
    }),
    VitePluginFonts({
      google: {
        families: ['Rubik']
      },
    })
  ]
})
