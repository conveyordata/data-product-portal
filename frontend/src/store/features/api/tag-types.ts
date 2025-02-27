export enum TagTypes {
    DataProduct = 'DataProduct',
    UserDataProducts = 'UserDataProducts',
    UserDatasets = 'UserDatasets',
    UserDataOutputs = 'UserDataOutputs',
    DataProductType = 'DataProductType',
    Tags = 'Tags',
    DataProductLifecycle = 'DataProductLifecycle',
    DataProductSetting = 'DataProductSetting',
    User = 'User',
    Auth = 'Auth',
    Environment = 'Environment',
    Dataset = 'Dataset',
    Domain = 'Domain',
    DataOutput = 'DataOutput',
    Platform = 'Platform',
    PlatformService = 'PlatformService',
    PlatformServiceConfig = 'PlatformServiceConfig',
    EnvironmentConfigs = 'EnvironmentConfigs',
    Version = 'Version',
    AI = 'AI',
}

export const STATIC_TAG_ID = {
    LIST: 'LIST',
} as const;
