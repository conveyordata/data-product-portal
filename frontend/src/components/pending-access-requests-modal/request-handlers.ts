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

export async function acceptRequest(request: Request, handlers: ActionHandlers, decisionNote?: string): Promise<void> {
    switch (request.request_type) {
        case RequestType_InputPort:
            return handlers.handleAcceptDataProductDatasetLink({
                dataProductId: request.input_port.output_port.data_product_id,
                outputPortId: request.input_port.output_port_id,
                approveOutputPortAsInputPortRequest: {
                    consuming_data_product_id: request.input_port.consuming_abstract_data_product_id,
                    decision_note: decisionNote,
                },
            });
        case RequestType_TechnicalAssetOutputPort:
            return handlers.handleAcceptDataOutputDatasetLink({
                dataProductId: request.output_port.data_product_id,
                outputPortId: request.output_port_id,
                approveLinkBetweenTechnicalAssetAndOutputPortRequest: {
                    technical_asset_id: request.technical_asset_id,
                },
            });
        case RequestType_DataProductRoleAssignment:
            return handlers.handleGrantAccessToDataProduct({
                assignment_id: request.id,
                data_product_id: request.data_product.id,
            });
    }
}

export async function rejectRequest(request: Request, handlers: ActionHandlers, decisionNote?: string): Promise<void> {
    switch (request.request_type) {
        case RequestType_InputPort:
            if (!decisionNote) {
                throw new Error('Decision note is required to reject a request');
            }
            return handlers.handleRejectDataProductDatasetLink({
                dataProductId: request.input_port.output_port.data_product_id,
                outputPortId: request.input_port.output_port_id,
                denyOutputPortAsInputPortRequest: {
                    consuming_data_product_id: request.input_port.consuming_abstract_data_product_id,
                    decision_note: decisionNote,
                },
            });
        case RequestType_TechnicalAssetOutputPort:
            return handlers.handleRejectDataOutputDatasetLink({
                dataProductId: request.output_port.data_product_id,
                outputPortId: request.output_port_id,
                denyLinkBetweenTechnicalAssetAndOutputPortRequest: {
                    technical_asset_id: request.technical_asset_id,
                },
            });
        case RequestType_DataProductRoleAssignment:
            return handlers.handleDenyAccessToDataProduct({
                assignment_id: request.id,
                data_product_id: request.data_product.id,
            });
    }
}
