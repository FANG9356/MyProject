import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    host: true, 
    allowedHosts: true, 
    open: false, 
    proxy: {
      '/api': {
        target: 'http://localhost:4282', 
        changeOrigin: false
      },
      '/uploads': {
        target: 'http://localhost:4282',
        changeOrigin: false
      }
    }
  },
  optimizeDeps: {
    force: true, 
    include: ['recharts', 'lodash'] 
  }
})