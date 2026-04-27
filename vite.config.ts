import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  base: '/', // <--- Alterado para a raiz
  
  // 👇 ADICIONADO: Aumenta o limite de aviso do Vite (tira o aviso amarelo do console)
  build: {
    chunkSizeWarningLimit: 5000, 
  },
  
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      devOptions: {
        enabled: true
      },
      // 👇 ADICIONADO: Diz ao PWA para aceitar arquivos de até 5MB no cache offline
      workbox: {
        maximumFileSizeToCacheInBytes: 5000000 
      },
      manifest: {
        id: '/', // <--- Alterado para a raiz
        name: 'ProvaPoP',
        short_name: 'ProvaPoP',
        description: 'Webgame musical ProvaPoP',
        lang: 'pt-BR',
        theme_color: '#111827',
        background_color: '#111827',
        display: 'standalone',
        start_url: '/', // <--- Alterado para a raiz
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable'
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        ws: true
      }
    }
  }
})
