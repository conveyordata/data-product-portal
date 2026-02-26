import type { PendingAction } from '@/types/pending-actions/pending-request-types';
import {
    type PendingRequestType,
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_DataProductRoleAssignment,
    PendingRequestType_TechnicalAssetOutputPort,
} from '@/types/pending-actions/pending-request-types';

export interface TableRow {
    key: string;
    pendingAction: PendingAction;
    description: string;
    requestedBy: { name: string; email: string };
    date: string;
    dataProductName?: string;
    outputPortName?: string;
}

/**
 * Returns a formatted description string for a pending action request
 * Examples:
 * - "Product Name requests read access to Output Name"
 * - "User Name requests Admin role"
 */
export function getRequestDescription(action: PendingAction): string {
    if (action.pending_action_type === PendingRequestType_DataProductOutputPort) {
        const productName = action.data_product.name;
        const outputPortName = action.output_port.name;
        return `${productName} requests read access to ${outputPortName}`;
    }

    if (action.pending_action_type === PendingRequestType_TechnicalAssetOutputPort) {
        const assetName = action.technical_asset.name;
        const outputPortName = action.output_port.name;
        return `${assetName} requests to be included in ${outputPortName}`;
    }

    if (action.pending_action_type === PendingRequestType_DataProductRoleAssignment) {
        const userName = `${action.user.first_name} ${action.user.last_name}`;
        const roleName = action.role?.name || 'role';
        const productName = action.data_product.name;
        return `${userName} requests the ${roleName} role for ${productName}`;
    }

    return '';
}

export function transformToTableRow(action: PendingAction): TableRow {
    const baseRow = {
        key: action.id,
        pendingAction: action,
    };

    if (action.pending_action_type === PendingRequestType_DataProductOutputPort) {
        return {
            ...baseRow,
            requestedBy: {
                name: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
                email: action.requested_by.email,
            },
            description: getRequestDescription(action),
            dataProductName: action.data_product.name,
            date: action.requested_on,
        };
    }

    if (action.pending_action_type === PendingRequestType_TechnicalAssetOutputPort) {
        return {
            ...baseRow,
            requestedBy: {
                name: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
                email: action.requested_by.email,
            },
            description: getRequestDescription(action),
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
            description: getRequestDescription(action),
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
        description: '',
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
