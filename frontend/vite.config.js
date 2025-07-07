import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: ['www.justforfun.com.cn'],
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
        followRedirects: true,
        rewrite: (path) => path,
        timeout: 10000,  // 减少超时时间，更快地失败
        configure: (proxy, options) => {
          // 设置重试次数
          let retries = {};
          const MAX_RETRIES = 2;

          proxy.on('error', (err, req, res) => {
            const url = req.url;
            console.log('代理错误', err);
            
            // 只有特定错误才尝试重试
            if ((err.code === 'ECONNREFUSED' || err.code === 'ECONNRESET') && 
                (!retries[url] || retries[url] < MAX_RETRIES)) {
              
              retries[url] = (retries[url] || 0) + 1;
              console.log(`重试请求 ${url} (${retries[url]}/${MAX_RETRIES})`);
              
              // 防止已关闭的响应
              if (!res.headersSent && !res.writableEnded) {
                // 返回错误响应而不是挂起
                res.writeHead(503, {
                  'Content-Type': 'application/json'
                });
                res.end(JSON.stringify({
                  error: 'Service temporarily unavailable',
                  message: 'Backend connection failed'
                }));
              }
            }
          });
          
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('代理请求', req.url);
          });
          
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('代理响应', req.url, proxyRes.statusCode);
            // 成功的请求清除重试计数
            if (retries[req.url]) {
              delete retries[req.url];
            }
          });
        }
      },
    },
  },
})
