export enum TagTypes {
    DataProduct = 'DataProduct',
    UserDataProducts = 'UserDataProducts',
    UserDatasets = 'UserDatasets',
    DataProductType = 'DataProductType',
    User = 'User',
    Auth = 'Auth',
    Environment = 'Environment',
    Dataset = 'Dataset',
    BusinessArea = 'BusinessArea',
    Platform = 'Platform',
    PlatformService = 'PlatformService',
    EnvironmentConfigs = 'EnvironmentConfigs',
}

export const STATIC_TAG_ID = {
    LIST: 'LIST',
} as const;
