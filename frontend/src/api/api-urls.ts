export enum ApiUrl {
    DataOutputs = '/api/data_outputs',
    DataOutputGet = '/api/data_outputs/:dataOutputId',
    DataOutputConfig = '/api/data_outputs/config',
    DataOutputsDataset = '/api/data_outputs/:dataOutputId/dataset/:datasetId',
    DataOutputsDatasets = '/api/data_outputs_dataset_links',
    DataOutputDatasetLinkApprove = '/api/data_output_dataset_links/approve/:datasetLinkId',
    DataOutputDatasetLinkReject = '/api/data_output_dataset_links/deny/:datasetLinkId',
    DataOutputDatasetLinkRemove = '/api/data_output_dataset_links/remove/:datasetLinkId',
    DataOutputDatasetPendingActions = '/api/data_output_dataset_links/actions',
    DataOutputGraph = '/api/data_outputs/:dataOutputId/graph',
    DataOutputHistory = '/api/data_outputs/:dataOutputId/history',
    DataOutputNamespaceSuggestion = '/api/data_outputs/namespace_suggestion',
    DataOutputNamespaceLimits = '/api/data_outputs/namespace_length_limits',
    DataOutputResultString = '/api/data_outputs/result_string',
    DataProducts = '/api/data_products',
    DataProductsDataOutput = '/api/data_products/:dataProductId/data_outputs',
    DataProductGet = '/api/data_products/:dataProductId',
    DataProductType = '/api/data_product_types',
    DataProductTypeId = '/api/data_product_types/:dataProductTypeId',
    DataProductTypeMigrate = '/api/data_product_types/migrate/:fromId/:toId',
    DataProductLifecycle = '/api/data_product_lifecycles',
    DataProductLifecycleGet = '/api/data_product_lifecycles/:lifecycleId',
    DataProductSetting = '/api/data_product_settings',
    DataProductSettingNamespaceValidation = '/api/data_product_settings/validate_namespace',
    DataProductSettingNamespaceSuggestion = '/api/data_product_settings/namespace_suggestion',
    DataProductSettingNamespaceLimits = '/api/data_product_settings/namespace_length_limits',
    DataProductOutputCreate = '/api/data_products/:dataProductId/data_output',
    DataProductSettingGet = '/api/data_product_settings/:settingId',
    DataProductSettingValue = '/api/data_products/:dataProductId/settings/:settingId',
    DataProductIntegrationUrl = '/api/data_products/:dataProductId/integration_url',
    DataProductDataset = '/api/data_products/:dataProductId/dataset/:datasetId',
    DataProductAbout = '/api/data_products/:dataProductId/about',
    DataProductHistory = '/api/data_products/:dataProductId/history',
    DataProductGraph = '/api/data_products/:dataProductId/graph',
    DataProductNamespaceValidation = '/api/data_products/validate_namespace',
    DataProductNamespaceSuggestion = '/api/data_products/namespace_suggestion',
    DataProductNamespaceLimits = '/api/data_products/namespace_length_limits',
    DataProductDataOutputNamespaceValidation = '/api/data_products/:dataProductId/data_output/validate_namespace',
    Users = '/api/users',
    UserDataProducts = '/api/data_products/user/:userId',
    UserDatasets = '/api/datasets/user/:userId',
    Authorize = '/api/auth/user',
    Roles = '/api/roles',
    RolesGet = '/api/roles/:scope',
    RolesDelete = '/api/roles/:roleId',
    RoleAssignmentsDataProductGet = '/api/role_assignments/data_product',
    RoleAssignmentsDataProduct = '/api/role_assignments/data_product/:assignmentId',
    RoleAssignmentsDataProductRequest = '/api/role_assignments/data_product/request/:dataProductId',
    RoleAssignmentsDataProductDecide = '/api/role_assignments/data_product/:assignmentId/decide',
    RoleAssignmentsDatasetGet = '/api/role_assignments/dataset',
    RoleAssignmentsDataset = '/api/role_assignments/dataset/:assignmentId',
    RoleAssignmentsDatasetRequest = '/api/role_assignments/dataset/request/:datasetId',
    RoleAssignmentsDatasetDecide = '/api/role_assignments/dataset/:assignmentId/decide',
    RoleAssignmentsGlobal = '/api/role_assignments/global',
    RoleAssignmentsGlobalDelete = '/api/role_assignments/global/:assignmentId',
    RoleAssignmentsGlobalRequest = '/api/role_assignments/global/request',
    RoleAssignmentsGlobalDecide = '/api/role_assignments/global/:assignmentId/decide',
    RoleAssignmentsGlobalUpdate = '/api/role_assignments/global/:assignmentId/role',
    Tags = '/api/tags',
    TagsId = '/api/tags/:tagId',
    Environments = '/api/envs',
    EnvironmentGet = '/api/envs/:environmentId',
    EnvPlatformServiceConfigs = '/api/envs/:environmentId/configs',
    EnvPlatformServiceConfig = '/api/envs/configs/:configId',
    EnvPlatformServiceConfigNoId = '/api/envs/configs',
    EnvPlatformServiceConfigId = '/api/envs/platforms/:platformId/services/:serviceId/config',
    Datasets = '/api/datasets',
    DatasetUser = '/api/datasets/:datasetId/user/:userId',
    DatasetGet = '/api/datasets/:datasetId',
    DatasetSettingValue = '/api/datasets/:datasetId/settings/:settingId',
    DatasetAbout = '/api/datasets/:datasetId/about',
    DatasetGraph = '/api/datasets/:datasetId/graph',
    DatasetIntegrationUrl = '/api/data_products/:dataProductId/integration_url',
    DatasetHistory = '/api/datasets/:datasetId/history',
    DatasetNamespaceValidation = '/api/datasets/validate_namespace',
    DatasetNamespaceSuggestion = '/api/datasets/namespace_suggestion',
    DatasetNamespaceLimits = '/api/datasets/namespace_length_limits',
    Domains = '/api/domains',
    DomainsId = '/api/domains/:domainId',
    DomainsMigrate = '/api/domains/migrate/:fromId/:toId',
    DataProductsDatasets = '/api/data_product_dataset_links',
    DataProductDatasetLinkApprove = '/api/data_product_dataset_links/approve/:datasetLinkId',
    DataProductDatasetLinkReject = '/api/data_product_dataset_links/deny/:datasetLinkId',
    DataProductDatasetLinkRemove = '/api/data_product_dataset_links/remove/:datasetLinkId',
    DataProductDatasetPendingActions = '/api/data_product_dataset_links/actions',
    PendingActions = '/api/pending_actions',
    Platforms = '/api/platforms',
    PlatformsConfigs = '/api/platforms/configs',
    PlatformServices = '/api/platforms/:platformId/services',
    PlatformServiceConfig = '/api/platforms/:platformId/services/:serviceId',
    PlatformServiceConfigById = '/api/platforms/configs/:configId',
    Version = '/api/version',
    ThemeSettings = '/api/theme_settings',
    AccessCheck = '/api/authz/access',
    AdminCheck = '/api/authz/admin',
    Graph = '/api/graph',
    Notifications = '/api/notifications',
    NotificationDelete = '/api/notifications/:notificationId',
    NotificationDeleteAll = '/api/notifications/all',
}

export type DynamicPathParams =
    | 'dataProductId'
    | 'dataProductTypeId'
    | 'dataOutputId'
    | 'datasetId'
    | 'datasetLinkId'
    | 'domainId'
    | 'fromId'
    | 'toId'
    | 'platformId'
    | 'serviceId'
    | 'environmentId'
    | 'settingId'
    | 'lifecycleId'
    | 'configId'
    | 'scope'
    | 'userId'
    | 'roleId'
    | 'assignmentId'
    | 'notificationId'
    | 'tagId';

export function buildUrl(url: string, pathParams: Partial<Record<DynamicPathParams, string>>): string {
    return Object.keys(pathParams).reduce((acc, key) => {
        const value = pathParams[key as DynamicPathParams];
        return value ? acc.replace(`:${key}`, value) : acc;
    }, url);
}
