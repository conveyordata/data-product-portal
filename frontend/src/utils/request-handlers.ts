import type { DataOutputDatasetLinkRequest } from '@/types/data-output-dataset';
import type { DataProductDatasetLinkRequest } from '@/types/data-product-dataset';
import { type PendingAction, PendingActionTypes } from '@/types/pending-actions/pending-actions';
import type { DataProductRoleRequest, DatasetRoleRequest } from './pending-request.helper';

type ActionHandlers = {
    handleAcceptDataProductDatasetLink: (req: DataProductDatasetLinkRequest) => Promise<void>;
    handleRejectDataProductDatasetLink: (req: DataProductDatasetLinkRequest) => Promise<void>;
    handleAcceptDataOutputDatasetLink: (req: DataOutputDatasetLinkRequest) => Promise<void>;
    handleRejectDataOutputDatasetLink: (req: DataOutputDatasetLinkRequest) => Promise<void>;
    handleGrantAccessToDataProduct: (req: DataProductRoleRequest) => Promise<void>;
    handleDenyAccessToDataProduct: (req: DataProductRoleRequest) => Promise<void>;
    handleGrantAccessToDataset: (req: DatasetRoleRequest) => Promise<void>;
    handleDenyAccessToDataset: (req: DatasetRoleRequest) => Promise<void>;
};

export async function acceptRequest(action: PendingAction, handlers: ActionHandlers): Promise<void> {
    switch (action.pending_action_type) {
        case PendingActionTypes.DataProductDataset:
            return handlers.handleAcceptDataProductDatasetLink({
                id: action.id,
                data_product_id: action.data_product_id,
                dataset_id: action.dataset_id,
            });
        case PendingActionTypes.DataOutputDataset:
            return handlers.handleAcceptDataOutputDatasetLink({
                id: action.id,
                data_output_id: action.data_output_id,
                dataset_id: action.dataset_id,
            });
        case PendingActionTypes.DataProductRoleAssignment:
            return handlers.handleGrantAccessToDataProduct({
                assignment_id: action.id,
                data_product_id: action.data_product.id,
            });
        case PendingActionTypes.DatasetRoleAssignment:
            return handlers.handleGrantAccessToDataset({
                assignment_id: action.id,
                dataset_id: action.output_port.id,
            });
    }
}

export async function rejectRequest(action: PendingAction, handlers: ActionHandlers): Promise<void> {
    switch (action.pending_action_type) {
        case PendingActionTypes.DataProductDataset:
            return handlers.handleRejectDataProductDatasetLink({
                id: action.id,
                data_product_id: action.data_product_id,
                dataset_id: action.dataset_id,
            });
        case PendingActionTypes.DataOutputDataset:
            return handlers.handleRejectDataOutputDatasetLink({
                id: action.id,
                data_output_id: action.data_output_id,
                dataset_id: action.dataset_id,
            });
        case PendingActionTypes.DataProductRoleAssignment:
            return handlers.handleDenyAccessToDataProduct({
                assignment_id: action.id,
                data_product_id: action.data_product.id,
            });
        case PendingActionTypes.DatasetRoleAssignment:
            return handlers.handleDenyAccessToDataset({
                assignment_id: action.id,
                dataset_id: action.output_port.id,
            });
    }
}
