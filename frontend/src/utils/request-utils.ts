import type { PendingAction } from '@/types/pending-actions/pending-actions';
import {
    type PendingRequestType,
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_DataProductRoleAssignment,
    PendingRequestType_TechnicalAssetOutputPort,
} from '@/types/pending-actions/pending-request-types';

export interface TableRow {
    key: string;
    pendingAction: PendingAction;
    requestedBy: { name: string; email: string };
    outputPortName: string;
    dataProductName: string;
    type: PendingRequestType | undefined;
    date: string;
    justification?: string;
}

export function transformToTableRow(action: PendingAction): TableRow {
    const baseRow = {
        key: action.id,
        pendingAction: action,
        type: action.pending_action_type,
    };

    if (action.pending_action_type === PendingRequestType_DataProductOutputPort) {
        return {
            ...baseRow,
            requestedBy: {
                name: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
                email: action.requested_by.email,
            },
            outputPortName: action.output_port.name,
            dataProductName: action.data_product.name,
            date: action.requested_on,
            justification: action.justification,
        };
    }

    if (action.pending_action_type === PendingRequestType_TechnicalAssetOutputPort) {
        return {
            ...baseRow,
            requestedBy: {
                name: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
                email: action.requested_by.email,
            },
            outputPortName: action.output_port.name,
            dataProductName: action.technical_asset.name,
            date: action.requested_on,
        };
    }

    if (action.pending_action_type === PendingRequestType_DataProductRoleAssignment) {
        return {
            ...baseRow,
            requestedBy: {
                name: `${action.user.first_name} ${action.user.last_name}`,
                email: action.user.email,
            },
            outputPortName: '-',
            dataProductName: action.data_product.name,
            date: action.requested_on || '',
        };
    }
    return {
        ...baseRow,
        requestedBy: {
            name: '',
            email: '',
        },
        outputPortName: '',
        dataProductName: '',
        date: '',
    };
}

export function getRequestLink(action: PendingAction): { dataProductId: string; datasetId?: string } | null {
    switch (action.pending_action_type) {
        case PendingRequestType_DataProductOutputPort:
            return {
                dataProductId: action.output_port.data_product_id,
                datasetId: action.output_port_id,
            };
        case PendingRequestType_TechnicalAssetOutputPort:
            return {
                dataProductId: action.technical_asset.owner_id,
                datasetId: action.output_port_id,
            };
        case PendingRequestType_DataProductRoleAssignment:
            return {
                dataProductId: action.data_product.id,
            };
        default:
            return null;
    }
}

export function isOutputPortRequest(type: PendingRequestType): boolean {
    return type === PendingRequestType_DataProductOutputPort || type === PendingRequestType_TechnicalAssetOutputPort;
}

export function isRoleRequest(type: PendingRequestType): boolean {
    return type === PendingRequestType_DataProductRoleAssignment;
}
