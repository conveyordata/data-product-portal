import type { DataOutputDatasetContract } from '../data-output-dataset';
import type { DataProductDatasetContract } from '../data-product-dataset';
import type { DataProductRoleAssignment, OutputPortRoleAssignment } from '../roles';

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

export interface DataProductRoleAssignmentPendingAction extends DataProductRoleAssignment {
    pending_action_type: PendingActionTypes.DataProductRoleAssignment;
}

export interface DatasetRoleAssignmentPendingAction extends OutputPortRoleAssignment {
    pending_action_type: PendingActionTypes.DatasetRoleAssignment;
}

export type PendingAction =
    | DataProductDatasetPendingAction
    | DataOutputDatasetPendingAction
    | DataProductRoleAssignmentPendingAction
    | DatasetRoleAssignmentPendingAction;
