import path from 'path';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import svgr from 'vite-plugin-svgr';

// https://vitejs.dev/config/
export default defineConfig(() => {
    return {
        resolve: {
            alias: {
                '@': path.resolve(__dirname, './src/'),
                '~@': path.resolve(__dirname, './src/'),
            },
        },
        plugins: [
            react(),
            svgr({
                svgrOptions: {
                    ref: true,
                    svgo: false,
                    titleProp: true,
                    icon: true,
                },
                include: '**/*.svg?react',
            }),
        ],
        server: {
            port: 3000,
            open: true,
        },
        preview: {
            port: 3000,
            open: true,
        },
        css: {
            preprocessorOptions: {
                scss: {
                    api: 'modern-compiler' as const,
                },
            },
            modules: {
                localsConvention: 'camelCase' as const,
            },
        },
    };
});
