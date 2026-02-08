import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    host: true,
    strictPort: false, // Allow trying different port if 3001 is taken
  },
  build: {
    outDir: 'dist',
  },
});