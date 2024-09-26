export enum ApplicationPaths {
    Home = '/',
    DataProducts = '/data-products',
    DataProduct = '/data-products/:dataProductId',
    DataProductNew = '/data-products/new',
    DataProductEdit = '/data-products/:dataProductId/edit',
    Datasets = '/datasets',
    Dataset = '/datasets/:datasetId',
    DatasetNew = '/datasets/new',
    DatasetEdit = '/datasets/:datasetId/edit',
    AuditLogs = '/audit-logs',
    Settings = '/settings',
    Logout = '/logout',
}

export const authenticatedPaths: string[] = [
    ApplicationPaths.Home,
    ApplicationPaths.DataProducts,
    ApplicationPaths.DataProduct,
    ApplicationPaths.DataProductNew,
    ApplicationPaths.DataProductEdit,
    ApplicationPaths.Datasets,
    ApplicationPaths.Dataset,
    ApplicationPaths.AuditLogs,
    ApplicationPaths.Settings,
];

export function createDataProductIdPath(dataProductId: string) {
    return ApplicationPaths.DataProduct.replace(':dataProductId', encodeURIComponent(dataProductId));
}

export function createDatasetIdPath(datasetId: string) {
    return ApplicationPaths.Dataset.replace(':datasetId', encodeURIComponent(datasetId));
}

export enum DynamicPathParams {
    DataProductId = 'dataProductId',
    DatasetId = 'datasetId',
}

export enum ApplicationPageTitles {
    Home = 'Home',
    DataProducts = 'DataProducts',
    DataProduct = 'DataProduct',
    Datasets = 'Datasets',
    Dataset = 'Dataset',
    AuditLogs = 'Audit Logs',
    Settings = 'Settings',
}
