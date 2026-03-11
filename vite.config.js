import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { nodePolyfills } from 'vite-plugin-node-polyfills'

export default defineConfig({
  plugins: [
    vue(),
    nodePolyfills({
      // 启用所有 polyfill
      protocolImports: true,
      include: ['process', 'buffer', 'stream', 'util'],
      globals: {
        process: true,
        Buffer: true,
      },
    }),
  ],
  define: {
    'process.env': {}, // 提供空环境变量
  },
  optimizeDeps: {
    esbuildOptions: {
      define: {
        global: 'globalThis', // 解决 global 未定义问题
      },
    },
  },
})