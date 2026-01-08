import { TabKeys as DataOutputTabKeys } from '@/pages/data-output/components/data-output-tabs/data-output-tabkeys';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';

export enum ApplicationPaths {
    Home = '/',
    DataProducts = '/data-products',
    Documentation = '/documentation',
    DataProduct = '/data-products/:dataProductId',
    DataProductNew = '/data-products/new',
    DataProductEdit = '/data-products/:dataProductId/edit',
    Datasets = '/datasets',
    Dataset = '/datasets/:datasetId',
    DatasetEdit = '/datasets/:datasetId/edit',
    Marketplace = '/marketplace',
    MarketplaceCart = '/marketplace/cart',
    DataOutput = '/data-products/:dataProductId/:dataOutputId',
    DataOutputEdit = '/data-products/:dataProductId/:dataOutputId/edit',
    AuditLogs = '/audit-logs',
    Explorer = '/explorer',
    Logout = '/logout',
    Settings = '/settings',
    People = '/people',
}

export function createDataProductIdPath(
    dataProductId: string,
    tabKey: DataProductTabKeys = DataProductTabKeys.About,
): string {
    return `${ApplicationPaths.DataProduct.replace(':dataProductId', encodeURIComponent(dataProductId))}#${tabKey}`;
}

export function createDataOutputIdPath(
    dataOutputId: string,
    dataProductId: string,
    tabKey: DataOutputTabKeys = DataOutputTabKeys.Datasets,
) {
    return `${ApplicationPaths.DataOutput.replace(':dataProductId', encodeURIComponent(dataProductId)).replace(
        ':dataOutputId',
        encodeURIComponent(dataOutputId),
    )}#${tabKey}`;
}

export function createDatasetIdPath(datasetId: string, tabKey: DatasetTabKeys = DatasetTabKeys.About) {
    return `${ApplicationPaths.Dataset.replace(':datasetId', encodeURIComponent(datasetId))}#${tabKey}`;
}

export enum DynamicPathParams {
    DataProductId = 'dataProductId',
    DataOutputId = 'dataOutputId',
    DatasetId = 'datasetId',
    EnvironmentId = 'environmentId',
    EnvConfigId = 'envConfigId',
}
