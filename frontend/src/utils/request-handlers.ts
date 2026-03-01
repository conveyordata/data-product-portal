import type {
    ApproveOutputPortAsInputPortApiArg,
    DenyOutputPortAsInputPortApiArg,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi';
import type {
    ApproveOutputPortTechnicalAssetLinkApiArg,
    DenyOutputPortTechnicalAssetLinkApiArg,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi';
import type { PendingAction } from '@/types/pending-actions/pending-request-types';
import {
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_DataProductRoleAssignment,
    PendingRequestType_TechnicalAssetOutputPort,
} from '@/types/pending-actions/pending-request-types';
import type { DataProductRoleRequest } from './pending-request.helper';

type ActionHandlers = {
    handleAcceptDataProductDatasetLink: (req: ApproveOutputPortAsInputPortApiArg) => Promise<void>;
    handleRejectDataProductDatasetLink: (req: DenyOutputPortAsInputPortApiArg) => Promise<void>;
    handleAcceptDataOutputDatasetLink: (req: ApproveOutputPortTechnicalAssetLinkApiArg) => Promise<void>;
    handleRejectDataOutputDatasetLink: (req: DenyOutputPortTechnicalAssetLinkApiArg) => Promise<void>;
    handleGrantAccessToDataProduct: (req: DataProductRoleRequest) => Promise<void>;
    handleDenyAccessToDataProduct: (req: DataProductRoleRequest) => Promise<void>;
};

export async function acceptRequest(action: PendingAction, handlers: ActionHandlers): Promise<void> {
    switch (action.pending_action_type) {
        case PendingRequestType_DataProductOutputPort:
            return handlers.handleAcceptDataProductDatasetLink({
                dataProductId: action.output_port.data_product_id,
                outputPortId: action.output_port_id,
                approveOutputPortAsInputPortRequest: {
                    consuming_data_product_id: action.data_product_id,
                },
            });
        case PendingRequestType_TechnicalAssetOutputPort:
            return handlers.handleAcceptDataOutputDatasetLink({
                dataProductId: action.output_port.data_product_id,
                outputPortId: action.output_port_id,
                approveLinkBetweenTechnicalAssetAndOutputPortRequest: {
                    technical_asset_id: action.technical_asset_id,
                },
            });
        case PendingRequestType_DataProductRoleAssignment:
            return handlers.handleGrantAccessToDataProduct({
                assignment_id: action.id,
                data_product_id: action.data_product.id,
            });
    }
}

export async function rejectRequest(action: PendingAction, handlers: ActionHandlers): Promise<void> {
    switch (action.pending_action_type) {
        case PendingRequestType_DataProductOutputPort:
            return handlers.handleRejectDataProductDatasetLink({
                dataProductId: action.output_port.data_product_id,
                outputPortId: action.output_port_id,
                denyOutputPortAsInputPortRequest: {
                    consuming_data_product_id: action.data_product_id,
                },
            });
        case PendingRequestType_TechnicalAssetOutputPort:
            return handlers.handleRejectDataOutputDatasetLink({
                dataProductId: action.output_port.data_product_id,
                outputPortId: action.output_port_id,
                denyLinkBetweenTechnicalAssetAndOutputPortRequest: {
                    technical_asset_id: action.technical_asset_id,
                },
            });
        case PendingRequestType_DataProductRoleAssignment:
            return handlers.handleDenyAccessToDataProduct({
                assignment_id: action.id,
                data_product_id: action.data_product.id,
            });
    }
}
