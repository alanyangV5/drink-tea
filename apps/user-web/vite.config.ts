import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['tea-mist.svg'],
      manifest: {
        name: '来喝茶',
        short_name: '来喝茶',
        description: '极简卡片流探索茶叶，双向反馈驱动个性化推荐。',
        theme_color: '#FFFDF9',
        background_color: '#FFFDF9',
        display: 'standalone',
        icons: [{ src: '/pwa.svg', sizes: '512x512', type: 'image/svg+xml' }]
      },
      workbox: {
        runtimeCaching: [
          {
            urlPattern: ({ url }) => url.pathname.startsWith('/api/teas'),
            handler: 'NetworkFirst',
            options: { cacheName: 'api-teas', expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 * 7 } }
          },
          {
            urlPattern: ({ request }) => request.destination === 'image',
            handler: 'CacheFirst',
            options: { cacheName: 'images', expiration: { maxEntries: 60, maxAgeSeconds: 60 * 60 * 24 * 30 } }
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
    host: '0.0.0.0',
    allowedHosts: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
