export enum ApiUrl {
    DataOutputs = '/api/data_outputs',
    DataOutputGet = '/api/data_outputs/:dataOutputId',
    DataOutputsDataset = '/api/data_outputs/:dataOutputId/dataset/:datasetId',
    DataOutputsDatasets = '/api/data_outputs_dataset_links',
    DataOutputDatasetLinkApprove = '/api/data_output_dataset_links/approve/:datasetLinkId',
    DataOutputDatasetLinkReject = '/api/data_output_dataset_links/deny/:datasetLinkId',
    DataOutputDatasetLinkRemove = '/api/data_output_dataset_links/remove/:datasetLinkId',
    DataProducts = '/api/data_products',
    DataProductsDataOutput = '/api/data_products/:dataProductId/data_outputs',
    DataProductGet = '/api/data_products/:dataProductId',
    DataProductType = '/api/data_product_types',
    DataProductSignInUrl = '/api/data_products/:dataProductId/signin_url',
    DataProductConveyorNotebookUrl = '/api/data_products/:dataProductId/conveyor_notebook_url',
    DataProductConveyorIdeUrl = '/api/data_products/:dataProductId/conveyor_ide_url',
    DataProductDatabricksWorkspaceUrl = '/api/data_products/:dataProductId/databricks_workspace_url',
    DataProductDataset = '/api/data_products/:dataProductId/dataset/:datasetId',
    DataProductAbout = '/api/data_products/:dataProductId/about',
    DataProductGraph = '/api/data_products/:dataProductId/graph',
    DataProductMembershipAdd = '/api/data_product_memberships/create',
    DataProductMembershipUpdate = '/api/data_product_memberships/:membershipId/role',
    DataProductMembershipRequest = '/api/data_product_memberships/request',
    DataProductMembershipApprove = '/api/data_product_memberships/:membershipId/approve',
    DataProductMembershipDeny = '/api/data_product_memberships/:membershipId/deny',
    DataProductMembershipRemove = '/api/data_product_memberships/:membershipId/remove',
    Users = '/api/users',
    UserDataProducts = '/api/data_products/user/:userId',
    UserDatasets = '/api/datasets/user/:userId',
    Authorize = '/api/auth/user',
    Environments = '/api/envs',
    EnvironmentGet = '/api/envs/:environmentId',
    EnvPlatformServiceConfigs = '/api/envs/:environmentId/configs',
    EnvPlatformServiceConfig = '/api/envs/configs/:configId',
    EnvPlatformServiceConfigNoId = '/api/envs/configs',
    EnvPlatformServiceConfigId = '/api/envs/platforms/:platformId/services/:serviceId/config',
    Datasets = '/api/datasets',
    DatasetUser = '/api/datasets/:datasetId/user/:userId',
    DatasetGet = '/api/datasets/:datasetId',
    DatasetAbout = '/api/datasets/:datasetId/about',
    DatasetGraph = '/api/datasets/:datasetId/graph',
    BusinessAreas = '/api/business_areas',
    DataProductsDatasets = '/api/data_product_dataset_links',
    DataProductDatasetLinkApprove = '/api/data_product_dataset_links/approve/:datasetLinkId',
    DataProductDatasetLinkReject = '/api/data_product_dataset_links/deny/:datasetLinkId',
    DataProductDatasetLinkRemove = '/api/data_product_dataset_links/remove/:datasetLinkId',
    Platforms = '/api/platforms',
    PlatformsConfigs = '/api/platforms/configs',
    PlatformServices = '/api/platforms/:platformId/services',
    PlatformServiceConfig = '/api/platforms/:platformId/services/:serviceId',
    PlatformServiceConfigById = '/api/platforms/configs/:configId',
    Version = '/api/version',
}

export type DynamicPathParams =
    | 'dataProductId'
    | 'userId'
    | 'datasetId'
    | 'datasetLinkId'
    | 'membershipId'
    | 'platformId'
    | 'serviceId'
    | 'environmentId'
    | 'configId';

export function buildUrl(url: string, pathParams: Record<DynamicPathParams | string, string>): string {
    return Object.keys(pathParams).reduce((acc, key) => acc.replace(`:${key}`, pathParams[key]), url);
}
