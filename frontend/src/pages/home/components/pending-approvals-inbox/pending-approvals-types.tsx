export const PendingRequestType_DataProductOutputPort = 'DataProductOutputPort';
export const PendingRequestType_TechnicalAssetOutputPort = 'TechnicalAssetOutputPort';
export const PendingRequestType_DataProductRoleAssignment = 'DataProductRoleAssignment';
export const PendingRequestTypeValues = [
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_TechnicalAssetOutputPort,
    PendingRequestType_DataProductRoleAssignment,
] as const;

export type PendingRequestType = (typeof PendingRequestTypeValues)[number];
