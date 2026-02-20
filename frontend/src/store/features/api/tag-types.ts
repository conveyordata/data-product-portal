export enum TagTypes {
    DataProduct = 'DataProduct',
    UserDataProducts = 'UserDataProducts',
    UserDatasets = 'UserDatasets',
    UserDataOutputs = 'UserDataOutputs',
    DataProductSetting = 'DataProductSetting',
    Dataset = 'Dataset',
    DataOutput = 'DataOutput',
    History = 'History',
}

export const STATIC_TAG_ID = {
    LIST: 'LIST',
} as const;
