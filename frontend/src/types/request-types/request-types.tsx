import type {
    DataProductRoleAssignmentRequest,
    InputPortRequest,
    TechnicalAssetOutputPortRequest,
} from '@/store/api/services/generated/usersApi.ts';

export type Request = InputPortRequest | TechnicalAssetOutputPortRequest | DataProductRoleAssignmentRequest;

export const RequestType_InputPort = 'InputPort';
export const RequestType_TechnicalAssetOutputPort = 'TechnicalAssetOutputPort';
export const RequestType_DataProductRoleAssignment = 'DataProductRoleAssignment';
