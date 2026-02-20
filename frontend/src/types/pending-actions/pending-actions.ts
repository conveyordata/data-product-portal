import type {
    DataProductOutputPortPendingAction,
    DataProductRoleAssignmentPendingAction,
    TechnicalAssetOutputPortPendingAction,
} from '@/store/api/services/generated/usersApi';

export type PendingAction =
    | DataProductOutputPortPendingAction
    | TechnicalAssetOutputPortPendingAction
    | DataProductRoleAssignmentPendingAction;
