import { ApplicationPaths, DynamicPathParams } from '@/types/navigation.ts';

export function getDynamicRoutePath(path: string, param: DynamicPathParams, value: string) {
    return path.replace(`:${param}`, value);
}

export function isDataProductEditPage(path: string, dataProductId: string) {
    return (
        getDynamicRoutePath(ApplicationPaths.DataProductEdit, DynamicPathParams.DataProductId, dataProductId) === path
    );
}

export function isDatasetEditPage(path: string, datasetId?: string, dataProductId?: string) {
    if (!datasetId || !dataProductId) {
        return false;
    }
    return (
        path ===
        ApplicationPaths.MarketPlaceOutputPortEdit.replace(`:${DynamicPathParams.DatasetId}`, datasetId).replace(
            `:${DynamicPathParams.DataProductId}`,
            dataProductId,
        )
    );
}

export function isProductStudioOutputPortEditPage(path: string, datasetId: string, dataProductId: string) {
    return (
        path ===
        ApplicationPaths.OutputPortEdit.replace(`:${DynamicPathParams.DatasetId}`, datasetId).replace(
            `:${DynamicPathParams.DataProductId}`,
            dataProductId,
        )
    );
}

export function isDataOutputEditPage(path: string, dataOutputId: string, dataProductId: string) {
    return (
        getDynamicRoutePath(ApplicationPaths.DataOutputEdit, DynamicPathParams.DataOutputId, dataOutputId).replace(
            `:${DynamicPathParams.DataProductId}`,
            dataProductId,
        ) === path
    );
}
