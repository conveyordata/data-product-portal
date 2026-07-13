import type { User } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import type { DecisionStatus } from '@/store/api/services/generated/usersApi.ts';
import type { Request } from '@/types/request-types/request-types.tsx';
import {
    RequestType_DataProductRoleAssignment,
    RequestType_InputPort,
    RequestType_TechnicalAssetOutputPort,
} from '@/types/request-types/request-types.tsx';

export interface TableRow {
    key: string;
    pendingAction: Request;
    description: string;
    requestedBy: User | null;
    decidedBy: User | null;
    date: string;
    decision: DecisionStatus;
    decisionNote: string | null;
}

export function getRequestDescription(action: Request): string {
    switch (action.request_type) {
        case RequestType_InputPort:
            return `${action.consuming_abstract_data_product.name} requests read access to ${action.output_port.name}`;
        case RequestType_TechnicalAssetOutputPort:
            return `${action.technical_asset.name} requests to be included in ${action.output_port.name}`;
        case RequestType_DataProductRoleAssignment: {
            const userName = `${action.user.first_name} ${action.user.last_name}`;
            const roleName = action.role?.name || 'role';
            const productName = action.data_product.name;
            return `${userName} requests the ${roleName} role for ${productName}`;
        }
        default:
            throw new Error('Unknown request type');
    }
}

export function transformToTableRow(action: Request): TableRow {
    const baseRow = {
        key: action.id,
        pendingAction: action,
    };

    switch (action.request_type) {
        case RequestType_InputPort:
            return {
                ...baseRow,
                requestedBy: action.requested_by,
                decidedBy: action.approved_by ?? action.denied_by,
                description: getRequestDescription(action),
                date: action.requested_on,
                decision: action.status,
                decisionNote: action.decision_note,
            };
        case RequestType_TechnicalAssetOutputPort:
            return {
                ...baseRow,
                requestedBy: action.requested_by,
                decidedBy: action.approved_by ?? action.denied_by,
                description: getRequestDescription(action),
                date: action.requested_on,
                decision: action.status,
                decisionNote: null,
            };
        case RequestType_DataProductRoleAssignment:
            return {
                ...baseRow,
                requestedBy: action.requested_by,
                decidedBy: action.decided_by,
                description: getRequestDescription(action),
                date: action.requested_on || '',
                decision: action.decision,
                decisionNote: null,
            };
        default:
            throw new Error('Unknown request type');
    }
}
