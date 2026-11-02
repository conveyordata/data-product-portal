import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { createTestStore, waitFor } from '@/tests/test-utils.tsx';

describe('Data Product role assignment tags', () => {
    it('refreshes the role assignments and history when a role is requested', async () => {
        const calls = { roleAssignments: 0, history: 0 };
        server.use(
            http.get('*/api/v2/authz/role_assignments/data_product', () => {
                calls.roleAssignments++;
                return HttpResponse.json({ role_assignments: [] });
            }),
            http.get('*/api/v2/data_products/dp1/history', () => {
                calls.history++;
                return HttpResponse.json({ events: [] });
            }),
            http.post('*/api/v2/authz/role_assignments/data_product/request', () => HttpResponse.json({ id: 'ra1' })),
        );
        const store = createTestStore();
        store.dispatch(api.endpoints.listDataProductRoleAssignments.initiate({ dataProductId: 'dp1' }));
        store.dispatch(api.endpoints.getDataProductEventHistory.initiate('dp1'));
        await waitFor(() => expect(calls).toEqual({ roleAssignments: 1, history: 1 }));

        await store.dispatch(
            api.endpoints.requestDataProductRoleAssignment.initiate({
                user_id: 'u1',
                role_id: 'r1',
                data_product_id: 'dp1',
            }),
        );

        await waitFor(() => expect(calls).toEqual({ roleAssignments: 2, history: 2 }));
    });
});

describe('Output Port role assignment tags', () => {
    it('refreshes the role assignments and history when a role is requested', async () => {
        const calls = { roleAssignments: 0, history: 0 };
        server.use(
            http.get('*/api/v2/authz/role_assignments/output_port', () => {
                calls.roleAssignments++;
                return HttpResponse.json({ role_assignments: [] });
            }),
            http.get('*/api/v2/data_products/dp1/output_ports/op1/history', () => {
                calls.history++;
                return HttpResponse.json({ events: [] });
            }),
            http.post('*/api/v2/authz/role_assignments/output_port/request', () => HttpResponse.json({ id: 'ra1' })),
        );
        const store = createTestStore();
        store.dispatch(api.endpoints.listOutputPortRoleAssignments.initiate({ outputPortId: 'op1' }));
        store.dispatch(api.endpoints.getOutputPortsEventHistory.initiate({ dataProductId: 'dp1', id: 'op1' }));
        await waitFor(() => expect(calls).toEqual({ roleAssignments: 1, history: 1 }));

        await store.dispatch(
            api.endpoints.requestOutputPortRoleAssignment.initiate({
                user_id: 'u1',
                role_id: 'r1',
                output_port_id: 'op1',
            }),
        );

        await waitFor(() => expect(calls).toEqual({ roleAssignments: 2, history: 2 }));
    });
});
