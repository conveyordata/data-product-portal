export enum TagTypes {
    DataProduct = 'DataProduct',
    UserDataProducts = 'UserDataProducts',
    UserDatasets = 'UserDatasets',
    UserDataOutputs = 'UserDataOutputs',
    Tags = 'Tags',
    DataProductSetting = 'DataProductSetting',
    User = 'User',
    Auth = 'Auth',
    Role = 'Role',
    Environment = 'Environment',
    Dataset = 'Dataset',
    Domain = 'Domain',
    DataOutput = 'DataOutput',
    Graph = 'Graph',
    Platform = 'Platform',
    PlatformService = 'PlatformService',
    PlatformServiceConfig = 'PlatformServiceConfig',
    EnvironmentConfigs = 'EnvironmentConfigs',
    Version = 'Version',
    ThemeSettings = 'ThemeSettings',
    History = 'History',
    Notifications = 'Notifications',
}

export const STATIC_TAG_ID = {
    LIST: 'LIST',
} as const;
