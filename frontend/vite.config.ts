/// <reference types="vitest/config" />

import path from 'node:path';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';
import { defineConfig } from 'vite';
import svgr from 'vite-plugin-svgr';

// https://vitejs.dev/config/
export default defineConfig({
    test: {
        globals: true,
        environment: 'jsdom',
        environmentOptions: { jsdom: { url: 'http://localhost:8080' } },
        setupFiles: ['./src/tests/setup.ts'],
        testTimeout: 10000,
        // Every test file runs in a fresh process; pre-bundling these large barrel packages into
        // single files avoids re-reading thousands of small modules per test file.
        deps: {
            optimizer: {
                client: {
                    enabled: true,
                    // Bundled together so antd, the app and Testing Library share one copy of react-dom,
                    // icons and cssinjs (StyleProvider); a package left out would be loaded a second time.
                    include: [
                        'antd',
                        '@ant-design/icons',
                        '@ant-design/cssinjs',
                        'react-dom',
                        '@testing-library/react',
                        '@testing-library/dom',
                        '@testing-library/user-event',
                        'dayjs',
                        'date-fns',
                    ],
                },
            },
        },
        alias: [
            // Under Node, @ant-design/icons resolves to a CJS wrapper whose named exports get lost when
            // pre-bundled, so point the tests at its ESM build instead.
            {
                find: /^@ant-design\/icons$/,
                replacement: path.resolve(import.meta.dirname, './node_modules/@ant-design/icons/es/index.js'),
            },
        ],
    },
    resolve: {
        alias: {
            '@': path.resolve(import.meta.dirname, './src/'),
            '~@': path.resolve(import.meta.dirname, './src/'),
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
        visualizer({
            template: 'treemap',
            gzipSize: true,
            brotliSize: true,
            filename: 'dependencies.html',
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
        modules: {
            localsConvention: 'camelCase' as const,
        },
    },
});
