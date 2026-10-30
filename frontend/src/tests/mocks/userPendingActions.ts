import { HttpResponse, http } from 'msw';
import type {
    DataProductRoleAssignmentRequest,
    PendingActionResponse,
} from '@/store/api/services/generated/usersApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { notifiedUser } from '@/tests/mocks/userNotifications.ts';
import { RequestType_DataProductRoleAssignment } from '@/types/request-types/request-types.tsx';
import { DecisionStatus } from '@/types/roles';

export function roleAssignmentRequest(id: string, dataProductName: string): DataProductRoleAssignmentRequest {
    return {
        id,
        data_product: {
            id: `data-product-${id}`,
            name: dataProductName,
            namespace: `data-product-${id}`,
            description: '',
            status: 'active',
            type: { id: 'type', name: 'Analytics', description: '', icon_key: 'reporting' },
        },
        user: notifiedUser,
        role: null,
        decision: DecisionStatus.Pending,
        requested_on: '2026-10-26T10:00:00',
        requested_by: notifiedUser,
        decided_on: null,
        decided_by: null,
        request_type: RequestType_DataProductRoleAssignment,
    };
}

export function mockUserPendingActions(pendingActions: DataProductRoleAssignmentRequest[]) {
    server.use(
        http.get('*/api/v2/users/current/pending_actions', () =>
            HttpResponse.json({ pending_actions: pendingActions } satisfies PendingActionResponse),
        ),
    );
}
