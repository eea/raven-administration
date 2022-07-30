import { defineConfig } from 'vite'
import Vue from '@vitejs/plugin-vue'
import Components from "unplugin-vue-components/vite"
import AutoImport from "unplugin-auto-import/vite"
import UnoCSS from "unocss/vite"
import { presetUno, presetAttributify, presetIcons } from 'unocss'
import transformerDirective from '@unocss/transformer-directives'
import { VitePluginFonts } from 'vite-plugin-fonts'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    Vue(),
    Components(),
    AutoImport({
      imports: [
        'vue'
      ]
    }),
    VitePluginFonts({
      google: {
        families: ['Inter']
      },
    }),
    UnoCSS({
      presets: [
        presetUno(),
        presetAttributify(),
        presetIcons()
      ],
      transformers: [
        transformerDirective(),
      ],
      theme: {
        fontFamily: {
          'sans': ["Inter"]
        },
        colors: {
          'polar': {
            'a': '#2E3440',
            'b': '#3B4252',
            'c': '#434C5E',
            'd': '#4C566A',
          },
          'snow': {
            'a': '#D8DEE9',
            'b': '#E5E9F0',
            'c': '#ECEFF4',
            'd': '#EDEDEB',
          },
          'frost': {
            'a': '#EDEDEB',
            'b': '#88C0D0',
            'c': '#81A1C1',
            'd': '#5E81AC',
          },
          'aurora': {
            'a': '#BF616A',
            'b': '#D08770',
            'c': '#EBCB8B',
            'd': '#A3BE8C',
            'e': '#B48EAD',
          }
        }
      }
    })
  ]
})
