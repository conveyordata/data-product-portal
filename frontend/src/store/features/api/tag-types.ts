export enum TagTypes {
    DataProduct = 'DataProduct',
    UserDataProducts = 'UserDataProducts',
    UserDatasets = 'UserDatasets',
    DataProductType = 'DataProductType',
    Tags = 'Tags',
    User = 'User',
    Auth = 'Auth',
    Environment = 'Environment',
    Dataset = 'Dataset',
    BusinessArea = 'BusinessArea',
    DataOutput = 'DataOutput',
    Platform = 'Platform',
    PlatformService = 'PlatformService',
    PlatformServiceConfig = 'PlatformServiceConfig',
    EnvironmentConfigs = 'EnvironmentConfigs',
    Version = 'Version',
}

export const STATIC_TAG_ID = {
    LIST: 'LIST',
} as const;
