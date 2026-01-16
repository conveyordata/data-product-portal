import type { ConfigFile } from '@rtk-query/codegen-openapi';

const services = [
    { name: 'empty', file: 'empty' },
    { name: 'Authorization - Role assignments', file: 'authorizationRoleAssignments' },
    { name: 'Authorization - Roles', file: 'authorizationRoles' },
    { name: 'Users', file: 'users' },
    { name: 'Configuration - Data product lifecycles', file: 'configurationDataProductLifecycles' },
    { name: 'Configuration - Data product settings', file: 'configurationDataProductSettings' },
    { name: 'Configuration - Data product types', file: 'configurationDataProductTypes' },
    { name: 'Configuration - Domains', file: 'configurationDomains' },
    { name: 'Configuration - Environments', file: 'configurationEnvironments' },
    { name: 'Configuration - Platforms', file: 'configurationPlatforms' },
    { name: 'Configuration - Theme settings', file: 'configurationThemeSettings' },
    { name: 'Configuration - Tags', file: 'configurationTags' },
    { name: 'Plugins', file: 'plugins' },
    { name: 'CompleteService', file: 'completeService' }, // Always keep this as the last service otherwise the endpoint is not added to the complete service.
];

const outputFiles = {};

services.forEach(({ file, name }, i) => {
    if (i === 0) {
        return;
    }
    let apiFile = `@/store/api/services/generated/${services[i - 1].file}Api.ts`;
    if (i === 1) {
        apiFile = '@/store/api/services/baseApi.ts';
    }
    // @ts-expect-error
    outputFiles[`./services/generated/${file}Api.ts`] = {
        filterEndpoints: (
            _: string,
            operationDefinition: { operation: { tags?: string[] }; path: string },
        ): boolean => {
            return (
                (operationDefinition.operation.tags?.includes(name) && operationDefinition.path.includes('/v2')) ||
                false
            );
        },
        exportName: 'api',
        apiFile: apiFile,
        apiImport: 'api',
    };
});

const config: ConfigFile = {
    schemaFile: '../../../../docs/static/openapi.json',
    apiFile: './emptyApi.ts',
    apiImport: 'emptyApi',
    outputFiles,
    flattenArg: true,
    hooks: { queries: true, lazyQueries: true, mutations: true },
};

export default config;
