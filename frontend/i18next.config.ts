import { defineConfig } from 'i18next-cli';

export default defineConfig({
    locales: ['en'],
    extract: {
        input: 'src/**/*.{js,jsx,ts,tsx}',
        output: 'public/locales/{{language}}/{{namespace}}.json',
        defaultNS: 'translation',
        keySeparator: false,
        nsSeparator: false,
        functions: ['t', '*.t'],
        transComponents: ['Trans'],
    },
    types: {
        input: ['locales/{{language}}/{{namespace}}.json'],
        output: 'src/types/i18next.d.ts',
    },
});
