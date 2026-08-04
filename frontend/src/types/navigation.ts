import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { ExplorationTabKeys } from '@/pages/exploration/exploration-tab-keys.ts';
import { TabKeys as TechnicalAssetTabKeys } from '@/pages/technical-asset/components/technical-asset-tabs/technical-asset-tabkeys';
import { AbstractDataProductType } from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';

export enum ApplicationPaths {
    Home = '/',
    Studio = '/studio',
    DataProducts = '/data-products',
    Documentation = '/documentation',
    DataProduct = '/studio/:dataProductId',
    Exploration = '/studio/exploration/:explorationId',
    ExplorationEdit = '/studio/exploration/:explorationId/edit',
    DataProductNew = '/studio/new',
    DataProductEdit = '/studio/:dataProductId/edit',
    MarketPlaceOutputPort = '/marketplace/:dataProductId/datasets/:datasetId',
    MarketPlaceOutputPortEdit = '/marketplace/:dataProductId/datasets/:datasetId/edit',
    Marketplace = '/marketplace',
    MarketplaceCart = '/marketplace/cart',
    OutputPort = '/studio/:dataProductId/output-port/:datasetId',
    OutputPortEdit = '/studio/:dataProductId/output-port/:datasetId/edit',
    DataOutput = '/studio/:dataProductId/:dataOutputId',
    DataOutputEdit = '/studio/:dataProductId/:dataOutputId/edit',
    Explorer = '/explorer',
    Logout = '/logout',
    Settings = '/settings',
    People = '/people',
}

export function createDataProductIdPath(
    dataProductId: string,
    tabKey: DataProductTabKeys = DataProductTabKeys.About,
): string {
    return `${ApplicationPaths.DataProduct.replace(':dataProductId', encodeURIComponent(dataProductId))}?tab=${tabKey}`;
}

export function createExplorationIdPath(
    explorationId: string,
    tabKey: ExplorationTabKeys = ExplorationTabKeys.Start,
): string {
    return `${ApplicationPaths.Exploration.replace(':explorationId', encodeURIComponent(explorationId))}?tab=${tabKey}`;
}

export function createAbstractDataProductIdPath(id: string, type: AbstractDataProductType): string {
    if (type === AbstractDataProductType.DataProducts) {
        return createDataProductIdPath(id);
    }
    if (type === AbstractDataProductType.Explorations) {
        return createExplorationIdPath(id);
    }
    throw new Error(`Unknown AbstractDataProductType: ${type}`);
}

export function createDataOutputIdPath(
    dataOutputId: string,
    dataProductId: string,
    tabKey: TechnicalAssetTabKeys = TechnicalAssetTabKeys.OutputPorts,
) {
    return `${ApplicationPaths.DataOutput.replace(':dataProductId', encodeURIComponent(dataProductId)).replace(
        ':dataOutputId',
        encodeURIComponent(dataOutputId),
    )}?tab=${tabKey}`;
}

export function createMarketplaceOutputPortPath(
    datasetId: string,
    dataProductId: string,
    tabKey: DatasetTabKeys = DatasetTabKeys.About,
) {
    const url = ApplicationPaths.MarketPlaceOutputPort.replace(':datasetId', encodeURIComponent(datasetId)).replace(
        ':dataProductId',
        encodeURIComponent(dataProductId),
    );
    return `${url}?tab=${tabKey}`;
}

export function createOutputPortPath(
    dataProductId: string,
    datasetId: string,
    tabKey: DatasetTabKeys = DatasetTabKeys.About,
) {
    return `${ApplicationPaths.OutputPort.replace(':dataProductId', encodeURIComponent(dataProductId)).replace(
        ':datasetId',
        encodeURIComponent(datasetId),
    )}?tab=${tabKey}`;
}

export enum DynamicPathParams {
    DataProductId = 'dataProductId',
    ExplorationId = 'explorationId',
    DataOutputId = 'dataOutputId',
    DatasetId = 'datasetId',
    EnvironmentId = 'environmentId',
    EnvConfigId = 'envConfigId',
}
