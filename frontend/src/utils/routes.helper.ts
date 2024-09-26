import { ApplicationPaths, DynamicPathParams } from '@/types/navigation.ts';

export function getDynamicRoutePath(path: string, param: DynamicPathParams, value: string) {
    return path.replace(`:${param}`, value);
}

export function isDataProductEditPage(path: string, dataProductId: string) {
    return (
        getDynamicRoutePath(ApplicationPaths.DataProductEdit, DynamicPathParams.DataProductId, dataProductId) === path
    );
}
