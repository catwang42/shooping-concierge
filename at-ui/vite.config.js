import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { dirname, join } from 'node:path'

import basicSsl from '@vitejs/plugin-basic-ssl'

const currentDir = dirname(fileURLToPath(import.meta.url))

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    basicSsl(),
    {
      name: 'glsl',
      transform(code, id) {
        if (id.endsWith('.glsl')) {
          return {
            code: `export default ${JSON.stringify(code)};`,
            map: null,
          }
        }
      },
    },
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        quietDeps: true,
        additionalData: `@use "${join(currentDir, './src/styles/base.scss')}" as *;`,
        api: 'modern-compiler',
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },
})
