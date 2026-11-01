import { defineConfig } from 'vite';

// Development connects to a running API; the compiled frontend preview used
// by offline browser acceptance deliberately has no upstream backend. Its
// browser tests intercept /api via Playwright, and /live must not be proxied
// to a closed localhost:8080 socket (which previously logged ECONNREFUSED).
// Real WebSocket/PostgreSQL integration is tested separately against port 8080.
export default defineConfig({
  server: {
    proxy: {
      '/api': {target: 'http://localhost:8080', changeOrigin: true},
      '/live': {target: 'ws://localhost:8080', ws: true},
    },
  },
  preview: {proxy: {}},
});
