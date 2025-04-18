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
    Role = 'Role',
    Environment = 'Environment',
    Dataset = 'Dataset',
    Domain = 'Domain',
    DataOutput = 'DataOutput',
    Platform = 'Platform',
    PlatformService = 'PlatformService',
    PlatformServiceConfig = 'PlatformServiceConfig',
    EnvironmentConfigs = 'EnvironmentConfigs',
    Version = 'Version',
    ThemeSettings = 'ThemeSettings',
}

export const STATIC_TAG_ID = {
    LIST: 'LIST',
} as const;
