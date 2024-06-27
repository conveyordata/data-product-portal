export enum ApiUrl {
    DataProducts = '/api/data_products',
    DataProductGet = '/api/data_products/:dataProductId',
    DataProductType = '/api/data_product_types',
    DataProductSignInUrl = '/api/data_products/:dataProductId/signin_url',
    DataProductConveyorNotebookUrl = '/api/data_products/:dataProductId/conveyor_notebook_url',
    DataProductConveyorIdeUrl = '/api/data_products/:dataProductId/conveyor_ide_url',
    DataProductDataset = '/api/data_products/:dataProductId/dataset/:datasetId',
    DataProductAbout = '/api/data_products/:dataProductId/about',
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
    Datasets = '/api/datasets',
    DatasetUser = '/api/datasets/:datasetId/user/:userId',
    DatasetGet = '/api/datasets/:datasetId',
    DatasetAbout = '/api/datasets/:datasetId/about',
    BusinessAreas = '/api/business_areas',
    DataProductsDatasets = '/api/data_product_dataset_links',
    DataProductDatasetLinkApprove = '/api/data_product_dataset_links/approve/:datasetLinkId',
    DataProductDatasetLinkReject = '/api/data_product_dataset_links/deny/:datasetLinkId',
    DataProductDatasetLinkRemove = '/api/data_product_dataset_links/remove/:datasetLinkId',
}

export type DynamicPathParams = 'dataProductId' | 'userId' | 'datasetId' | 'datasetLinkId' | 'membershipId';

export function buildUrl(url: string, pathParams: Record<DynamicPathParams | string, string>): string {
    return Object.keys(pathParams).reduce((acc, key) => acc.replace(`:${key}`, pathParams[key]), url);
}
