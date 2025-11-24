import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Allow external network access (required for ngrok)
    port: 5173,
    // Ensure SPA routing works - serve index.html for all routes
    // This is the default behavior in Vite, but explicitly configured for clarity
    strictPort: false,
    // Allow ngrok and other external hosts
    allowedHosts: [
      '.ngrok-free.dev',
      '.ngrok.io',
      '.ngrok.app',
      'localhost',
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  // Build configuration for production
  build: {
    rollupOptions: {
      input: {
        main: './index.html',
      },
    },
  },
})

