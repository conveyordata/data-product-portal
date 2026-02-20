export enum ApiUrl {
    DataProductSettingValue = '/api/data_products/:dataProductId/settings/:settingId',
    DatasetSettingValue = '/api/datasets/:datasetId/settings/:settingId',
}

type DynamicPathParams =
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
