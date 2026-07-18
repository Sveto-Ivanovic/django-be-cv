import { fileURLToPath, URL } from 'node:url'
import {  ViteSSGOptions } from 'vite-ssg'
import vueDevTools from 'vite-plugin-vue-devtools'
import { defineConfig, UserConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
// vite.config.ts

export default defineConfig({
  plugins: [
    vue(),
   // vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  ssgOptions: {
    includedRoutes(paths, routes) {
        const publicPaths = ['/', '/about', '/contact']
      return paths.filter(p => publicPaths.includes(p))
    },
  }
} as UserConfig & { ssgOptions?: ViteSSGOptions })
