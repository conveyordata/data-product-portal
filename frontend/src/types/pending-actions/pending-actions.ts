import type { DataOutputDatasetContract, DataOutputDatasetLinkRequest } from '../data-output-dataset';
import type { DataProductDatasetContract, DataProductDatasetLinkRequest } from '../data-product-dataset';
import type { DataProductRoleRequest, DatasetRoleRequest } from '../roles';
import type { DataProductRoleAssignmentContract, DatasetRoleAssignmentContract } from '../roles/role.contract';

export enum PendingActionTypes {
    DataProductDataset = 'DataProductDataset',
    DataOutputDataset = 'DataOutputDataset',
    DataProductRoleAssignment = 'DataProductRoleAssignment',
    DatasetRoleAssignment = 'DatasetRoleAssignment',
}

export interface DataProductDatasetPendingAction extends DataProductDatasetContract {
    pending_action_type: PendingActionTypes.DataProductDataset;
}

export interface DataOutputDatasetPendingAction extends DataOutputDatasetContract {
    pending_action_type: PendingActionTypes.DataOutputDataset;
}

export interface DataProductRoleAssignmentPendingAction extends DataProductRoleAssignmentContract {
    pending_action_type: PendingActionTypes.DataProductRoleAssignment;
}

export interface DatasetRoleAssignmentPendingAction extends DatasetRoleAssignmentContract {
    pending_action_type: PendingActionTypes.DatasetRoleAssignment;
}

export type PendingAction =
    | DataProductDatasetPendingAction
    | DataOutputDatasetPendingAction
    | DataProductRoleAssignmentPendingAction
    | DatasetRoleAssignmentPendingAction;

export type ActionResolveRequest =
    | { type: PendingActionTypes.DataOutputDataset; request: DataOutputDatasetLinkRequest }
    | { type: PendingActionTypes.DataProductDataset; request: DataProductDatasetLinkRequest }
    | { type: PendingActionTypes.DataProductRoleAssignment; request: DataProductRoleRequest }
    | { type: PendingActionTypes.DatasetRoleAssignment; request: DatasetRoleRequest };
