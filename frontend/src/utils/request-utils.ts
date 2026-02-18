import { type PendingAction, PendingActionTypes } from '@/types/pending-actions/pending-actions';

export interface TableRow {
    key: string;
    pendingAction: PendingAction;
    requestedBy: { name: string; email: string };
    outputPortName: string;
    dataProductName: string;
    type: PendingActionTypes;
    date: string;
}

export function transformToTableRow(action: PendingAction): TableRow {
    const baseRow = {
        key: action.id,
        pendingAction: action,
        type: action.pending_action_type,
    };

    if (action.pending_action_type === PendingActionTypes.DataProductDataset) {
        return {
            ...baseRow,
            requestedBy: {
                name: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
                email: action.requested_by.email,
            },
            outputPortName: action.dataset.name,
            dataProductName: action.data_product.name,
            date: action.requested_on,
        };
    }

    if (action.pending_action_type === PendingActionTypes.DataOutputDataset) {
        return {
            ...baseRow,
            requestedBy: {
                name: `${action.requested_by.first_name} ${action.requested_by.last_name}`,
                email: action.requested_by.email,
            },
            outputPortName: action.dataset.name,
            dataProductName: action.data_output.name,
            date: action.requested_on,
        };
    }

    if (action.pending_action_type === PendingActionTypes.DataProductRoleAssignment) {
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

    // DatasetRoleAssignment
    return {
        ...baseRow,
        requestedBy: {
            name: `${action.user.first_name} ${action.user.last_name}`,
            email: action.user.email,
        },
        outputPortName: action.output_port.name,
        dataProductName: action.output_port.name,
        date: action.requested_on || '',
    };
}

export function getRequestLink(action: PendingAction): { dataProductId: string; datasetId?: string } | null {
    switch (action.pending_action_type) {
        case PendingActionTypes.DataProductDataset:
            return {
                dataProductId: action.dataset.data_product_id,
                datasetId: action.dataset_id,
            };
        case PendingActionTypes.DataOutputDataset:
            return {
                dataProductId: action.data_output.owner_id,
                datasetId: action.dataset_id,
            };
        case PendingActionTypes.DatasetRoleAssignment:
            return {
                dataProductId: action.output_port.data_product_id,
                datasetId: action.output_port.id,
            };
        case PendingActionTypes.DataProductRoleAssignment:
            return {
                dataProductId: action.data_product.id,
            };
        default:
            return null;
    }
}

export function isOutputPortRequest(type: PendingActionTypes): boolean {
    return type === PendingActionTypes.DataProductDataset || type === PendingActionTypes.DataOutputDataset;
}

export function isRoleRequest(type: PendingActionTypes): boolean {
    return type === PendingActionTypes.DataProductRoleAssignment || type === PendingActionTypes.DatasetRoleAssignment;
}
