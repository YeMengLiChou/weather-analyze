import { fileURLToPath, URL } from "node:url";
import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import { ElementPlusResolver } from "unplugin-vue-components/resolvers";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueJsx from "@vitejs/plugin-vue-jsx";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        vueJsx(),
        // auto import element-ui components
        AutoImport({
            resolvers: [ElementPlusResolver()],
        }),
        Components({
            resolvers: [ElementPlusResolver()],
        }),
    ],
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
    server: {
        open: true,
        host: '0.0.0.0',
        port: 5000,
        proxy: { // 本地开发环境通过代理实现跨域，生产环境使用 nginx 转发
          // 正则表达式写法
          '/api': {
            target: 'http://127.0.0.1:8080/', // 后端服务实际地址
            changeOrigin: true, 
            rewrite: (path) => path
          }
        }
      },
});
