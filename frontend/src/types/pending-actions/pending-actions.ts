import { DataOutputDatasetContract, DataOutputDatasetLinkRequest } from '../data-output-dataset';
import { DataProductDatasetContract, DataProductDatasetLinkRequest } from '../data-product-dataset';
import { DataProductMembershipRoleRequest } from '../data-product-membership';
import { DataProductRoleAssignmentContract } from '../roles/role.contract';

export enum PendingActionTypes {
    DataProductDataset = 'DataProductDataset',
    DataOutputDataset = 'DataOutputDataset',
    DataProductRoleAssignment = 'DataProductRoleAssignment',
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

export type PendingAction =
    | DataProductDatasetPendingAction
    | DataOutputDatasetPendingAction
    | DataProductRoleAssignmentPendingAction;

export type ActionResolveRequest =
    | { type: PendingActionTypes.DataOutputDataset; request: DataOutputDatasetLinkRequest }
    | { type: PendingActionTypes.DataProductDataset; request: DataProductDatasetLinkRequest }
    | { type: PendingActionTypes.DataProductRoleAssignment; request: DataProductMembershipRoleRequest };
