import type { ConfigFile } from '@rtk-query/codegen-openapi';

const services = [
    { name: 'empty', file: 'empty' },
    { name: 'Authorization - Role assignments', file: 'authorizationRoleAssignments' },
    { name: 'Authorization - Roles', file: 'authorizationRoles' },
    { name: 'Users', file: 'users' },
    { name: 'Users - Notifications', file: 'usersNotifications' },
    { name: 'Configuration - Data Product lifecycles', file: 'configurationDataProductLifecycles' },
    { name: 'Configuration - Data Product settings', file: 'configurationDataProductSettings' },
    { name: 'Configuration - Data Product types', file: 'configurationDataProductTypes' },
    { name: 'Configuration - Domains', file: 'configurationDomains' },
    { name: 'Configuration - Environments', file: 'configurationEnvironments' },
    { name: 'Configuration - Platforms', file: 'configurationPlatforms' },
    { name: 'Configuration - Theme settings', file: 'configurationThemeSettings' },
    { name: 'Configuration - Tags', file: 'configurationTags' },
    { name: 'Plugins', file: 'plugins' },
    { name: 'Data Products', file: 'dataProducts' },
    { name: 'Data Products - Technical assets', file: 'dataProductsTechnicalAssets' },
    { name: 'Data Products - Output ports', file: 'dataProductsOutputPorts' },
    { name: 'Data Products - Output ports - Input ports', file: 'dataProductsOutputPortsInputPorts' },
    { name: 'Data Products - Output Ports - Data Quality', file: 'dataProductsOutputPortsDataQuality' },
    { name: 'Resource names', file: 'resourceNames' },
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
        useEnumType: !(file === 'authorizationRoleAssignments' || file === 'authorizationRoles' || file === 'users'),
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
