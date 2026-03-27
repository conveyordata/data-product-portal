import type { User } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import type { PendingAction } from '@/types/pending-actions/pending-request-types';
import {
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_DataProductRoleAssignment,
    PendingRequestType_TechnicalAssetOutputPort,
} from '@/types/pending-actions/pending-request-types';

export interface TableRow {
    key: string;
    pendingAction: PendingAction;
    description: string;
    requestedBy: User | null;
    date: string;
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
            requestedBy: action.requested_by,
            description: getRequestDescription(action),
            date: action.requested_on,
        };
    }

    if (action.pending_action_type === PendingRequestType_TechnicalAssetOutputPort) {
        return {
            ...baseRow,
            requestedBy: action.requested_by,
            description: getRequestDescription(action),
            date: action.requested_on,
        };
    }

    if (action.pending_action_type === PendingRequestType_DataProductRoleAssignment) {
        return {
            ...baseRow,
            requestedBy: action.requested_by,
            description: getRequestDescription(action),
            date: action.requested_on || '',
        };
    }
    return {
        ...baseRow,
        requestedBy: action.requested_by,
        description: '',
        date: '',
    };
}
