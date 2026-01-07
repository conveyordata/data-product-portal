export enum ApiUrl {
    DataOutputs = '/api/data_outputs',
    DataOutputGet = '/api/data_outputs/:dataOutputId',
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
    DataProductSetting = '/api/data_product_settings',
    DataProductSettingNamespaceValidation = '/api/data_product_settings/validate_namespace',
    DataProductSettingNamespaceSuggestion = '/api/data_product_settings/namespace_suggestion',
    DataProductSettingNamespaceLimits = '/api/data_product_settings/namespace_length_limits',
    DataProductOutputCreate = '/api/data_products/:dataProductId/data_output',
    DataProductSettingGet = '/api/data_product_settings/:settingId',
    DataProductSettingValue = '/api/data_products/:dataProductId/settings/:settingId',
    DataProductSignInUrl = '/api/data_products/:dataProductId/signin_url',
    DataProductConveyorIdeUrl = '/api/data_products/:dataProductId/conveyor_ide_url',
    DataProductDatabricksWorkspaceUrl = '/api/data_products/:dataProductId/databricks_workspace_url',
    DataProductSnowflakeUrl = '/api/data_products/:dataProductId/snowflake_url',
    DataProductDataset = '/api/data_products/:dataProductId/dataset/:datasetId',
    DataProductLinkDatasets = '/api/data_products/:dataProductId/link_datasets',
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
    UserSeenTour = '/api/users/seen_tour',
    UserBecomeAdmin = '/api/users/set_can_become_admin',
    Authorize = '/api/auth/user',
    Tags = '/api/tags',
    TagsId = '/api/tags/:tagId',
    Environments = '/api/envs',
    EnvironmentGet = '/api/envs/:environmentId',
    EnvPlatformServiceConfigs = '/api/envs/:environmentId/configs',
    EnvPlatformServiceConfig = '/api/envs/configs/:configId',
    EnvPlatformServiceConfigNoId = '/api/envs/configs',
    EnvPlatformServiceConfigId = '/api/envs/platforms/:platformId/services/:serviceId/config',
    Datasets = '/api/datasets',
    DatasetSearch = '/api/datasets/search',
    DatasetUser = '/api/datasets/:datasetId/user/:userId',
    DatasetGet = '/api/datasets/:datasetId',
    DatasetSettingValue = '/api/datasets/:datasetId/settings/:settingId',
    DatasetAbout = '/api/datasets/:datasetId/about',
    DatasetGraph = '/api/datasets/:datasetId/graph',
    DatasetHistory = '/api/datasets/:datasetId/history',
    DatasetCuratedQueries = '/api/datasets/:datasetId/usage/curated_queries',
    DatasetNamespaceValidation = '/api/datasets/validate_namespace',
    DatasetNamespaceSuggestion = '/api/datasets/namespace_suggestion',
    DatasetNamespaceLimits = '/api/datasets/namespace_length_limits',
    DatasetQueryStats = '/api/datasets/:datasetId/query_stats',
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
