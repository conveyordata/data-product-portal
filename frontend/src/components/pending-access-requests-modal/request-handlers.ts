import type {
    ApproveOutputPortAsInputPortApiArg,
    DenyOutputPortAsInputPortApiArg,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import type {
    ApproveOutputPortTechnicalAssetLinkApiArg,
    DenyOutputPortTechnicalAssetLinkApiArg,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import {
    type Request,
    RequestType_DataProductRoleAssignment,
    RequestType_InputPort,
    RequestType_TechnicalAssetOutputPort,
} from '@/types/request-types/request-types.tsx';
import type { DataProductRoleRequest } from '@/utils/pending-request.helper.ts';

type ActionHandlers = {
    handleAcceptDataProductDatasetLink: (req: ApproveOutputPortAsInputPortApiArg) => Promise<void>;
    handleRejectDataProductDatasetLink: (req: DenyOutputPortAsInputPortApiArg) => Promise<void>;
    handleAcceptDataOutputDatasetLink: (req: ApproveOutputPortTechnicalAssetLinkApiArg) => Promise<void>;
    handleRejectDataOutputDatasetLink: (req: DenyOutputPortTechnicalAssetLinkApiArg) => Promise<void>;
    handleGrantAccessToDataProduct: (req: DataProductRoleRequest) => Promise<void>;
    handleDenyAccessToDataProduct: (req: DataProductRoleRequest) => Promise<void>;
};

export async function acceptRequest(action: Request, handlers: ActionHandlers, decisionNote?: string): Promise<void> {
    switch (action.request_type) {
        case RequestType_InputPort:
            return handlers.handleAcceptDataProductDatasetLink({
                dataProductId: action.output_port.data_product_id,
                outputPortId: action.output_port_id,
                approveOutputPortAsInputPortRequest: {
                    consuming_data_product_id: action.consuming_abstract_data_product_id,
                    decision_note: decisionNote,
                },
            });
        case RequestType_TechnicalAssetOutputPort:
            return handlers.handleAcceptDataOutputDatasetLink({
                dataProductId: action.output_port.data_product_id,
                outputPortId: action.output_port_id,
                approveLinkBetweenTechnicalAssetAndOutputPortRequest: {
                    technical_asset_id: action.technical_asset_id,
                },
            });
        case RequestType_DataProductRoleAssignment:
            return handlers.handleGrantAccessToDataProduct({
                assignment_id: action.id,
                data_product_id: action.data_product.id,
            });
    }
}

export async function rejectRequest(action: Request, handlers: ActionHandlers, decisionNote?: string): Promise<void> {
    switch (action.request_type) {
        case RequestType_InputPort:
            if (!decisionNote) {
                throw new Error('Decision note is required to reject a request');
            }
            return handlers.handleRejectDataProductDatasetLink({
                dataProductId: action.output_port.data_product_id,
                outputPortId: action.output_port_id,
                denyOutputPortAsInputPortRequest: {
                    consuming_data_product_id: action.consuming_abstract_data_product_id,
                    decision_note: decisionNote,
                },
            });
        case RequestType_TechnicalAssetOutputPort:
            return handlers.handleRejectDataOutputDatasetLink({
                dataProductId: action.output_port.data_product_id,
                outputPortId: action.output_port_id,
                denyLinkBetweenTechnicalAssetAndOutputPortRequest: {
                    technical_asset_id: action.technical_asset_id,
                },
            });
        case RequestType_DataProductRoleAssignment:
            return handlers.handleDenyAccessToDataProduct({
                assignment_id: action.id,
                data_product_id: action.data_product.id,
            });
    }
}
