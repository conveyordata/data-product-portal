import { ApplicationPaths, DynamicPathParams } from '@/types/navigation.ts';

export function getDynamicRoutePath(path: string, param: DynamicPathParams, value: string) {
    return path.replace(`:${param}`, value);
}

export function isDataProductEditPage(path: string, dataProductId: string) {
    return (
        getDynamicRoutePath(ApplicationPaths.DataProductEdit, DynamicPathParams.DataProductId, dataProductId) === path
    );
}

export function isDatasetEditPage(path: string, datasetId: string) {
    return getDynamicRoutePath(ApplicationPaths.DatasetEdit, DynamicPathParams.DatasetId, datasetId) === path;
}

export function isDataOutputEditPage(path: string, dataOutputId: string, dataProductId: string) {
    return (
        getDynamicRoutePath(ApplicationPaths.DataOutputEdit, DynamicPathParams.DataOutputId, dataOutputId).replace(
            `:${DynamicPathParams.DataProductId}`,
            dataProductId,
        ) === path
    );
}
