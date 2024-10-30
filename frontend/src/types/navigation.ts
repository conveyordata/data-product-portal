import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabs.tsx';
import { DatasetTab } from '@/pages/data-product/components/data-product-tabs/dataset-tab/dataset-tab';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabs.tsx';


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
    DataOutput = '/data-products/:dataProductId/:dataOutputId',
    DataOutputNew = '/data-outputs/new',
    DataOutputEdit = '/data-products/:dataProductId/:dataOutputId/edit',
    AuditLogs = '/audit-logs',
    // Settings = '/settings',
    Logout = '/logout',
    PlatformsConfigs = '/platforms-configs',
    PlatformServiceConfigNew = '/platforms-configs/new',
    PlatformServiceConfig = '/platforms-configs/:platformServiceConfigId',
    Environments = '/environments',
    EnvironmentConfigs = '/environments/:environmentId/configs',
    EnvironmentConfig = '/environments/configs/:envConfigId',
    EnvironmentConfigNew = '/environments/:environmentId/new',
    EnvironmentNew = '/environments/new',
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
    ApplicationPaths.DataOutput,
    ApplicationPaths.DataOutputEdit,
    // ApplicationPaths.Settings,
    ApplicationPaths.PlatformsConfigs,
    ApplicationPaths.PlatformServiceConfig,
    ApplicationPaths.PlatformServiceConfigNew,
    ApplicationPaths.Environments,
    ApplicationPaths.EnvironmentNew,
    ApplicationPaths.EnvironmentConfig,
    ApplicationPaths.EnvironmentConfigs,
    ApplicationPaths.EnvironmentConfigNew,
];

export function createDataProductIdPath(dataProductId: string) {
    return ApplicationPaths.DataProduct.replace(':dataProductId', encodeURIComponent(dataProductId)) + '#' + DataProductTabKeys.About;
}

export function createDataOutputIdPath(dataOutputId: string, dataProductId: string) {
    return ApplicationPaths.DataOutput.replace(':dataProductId', encodeURIComponent(dataProductId)).replace(':dataOutputId', encodeURIComponent(dataOutputId));
}

export function createDatasetIdPath(datasetId: string) {
    return ApplicationPaths.Dataset.replace(':datasetId', encodeURIComponent(datasetId)) + '#' + DatasetTabKeys.About;
}

export function createPlatformServiceConfigIdPath(platformServiceConfigId: string) {
    return ApplicationPaths.PlatformServiceConfig.replace(
        ':platformServiceConfigId',
        encodeURIComponent(platformServiceConfigId),
    );
}

export function createEnvironmentConfigsPath(environmentId: string) {
    return ApplicationPaths.EnvironmentConfigs.replace(':environmentId', encodeURIComponent(environmentId));
}

export function createEnvironmentConfigPath(envConfigId: string) {
    return ApplicationPaths.EnvironmentConfig.replace(':envConfigId', encodeURIComponent(envConfigId));
}

export enum DynamicPathParams {
    DataProductId = 'dataProductId',
    DataOutputId = 'dataOutputId',
    DatasetId = 'datasetId',
    PlatformServiceConfigId = 'platformServiceConfigId',
    EnvironmentId = 'environmentId',
    EnvConfigId = 'envConfigId',
}

export enum ApplicationPageTitles {
    Home = 'Home',
    DataProducts = 'DataProducts',
    DataProduct = 'DataProduct',
    Datasets = 'Datasets',
    Dataset = 'Dataset',
    AuditLogs = 'Audit Logs',
    // Settings = 'Settings',
}
