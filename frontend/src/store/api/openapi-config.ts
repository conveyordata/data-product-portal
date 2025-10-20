import type { ConfigFile } from '@rtk-query/codegen-openapi';

const services = [
    'empty',
    'authz',
    'datasets',
    'dataProducts',
    'dataProductTypes',
    'dataProductLifecycles',
    'dataProductSettings',
    'dataProductDatasetLinks',
    'dataOutputDatasetLinks',
    'dataOutputs',
    'domains',
    'environments',
    'platforms',
    'tags',
    'users',
    'roles',
    'roleAssignments',
    'themeSettings',
    'graph',
    'notifications',
    'pendingActions',
    'events',
    'auth',
    'deviceFlow',
    'mcp',
    'default',
    'completeService',
];

const outputFiles = {};

services.forEach((service, i) => {
    if (i === 0) {
        return;
    }
    let apiFile = `@/store/api/services/generated/${services[i - 1]}Api.ts`;
    if (i == 1) {
        apiFile = '@/store/api/services/baseApi.ts';
    }
    outputFiles[`./services/generated/${service}Api.ts`] = {
        filterEndpoints: [new RegExp(`${service}.*`, 'i')],
        exportName: 'api',
        apiFile: apiFile,
        apiImport: 'api',
    };
});

const config: ConfigFile = {
    schemaFile: '../../../openapi.json',
    apiFile: './emptyApi.ts',
    apiImport: 'emptyApi',
    outputFiles,
    hooks: { queries: true, lazyQueries: true, mutations: true },
};

export default config;
