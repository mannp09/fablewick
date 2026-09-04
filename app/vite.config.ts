import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// GitHub Pages serves this app from /fablewick/ off the repo root
// (library/ stays where old links point; this app lives alongside it).
export default defineConfig({
  base: '/fablewick/',
  plugins: [react()],
})
