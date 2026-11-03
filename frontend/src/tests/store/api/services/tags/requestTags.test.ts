import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { createTestStore, waitFor } from '@/tests/test-utils.tsx';

type Store = ReturnType<typeof createTestStore>;

describe('request list tags', () => {
    it.each<[string, (store: Store) => Promise<unknown>]>([
        [
            'cancelling an Input Port request',
            (store) =>
                store.dispatch(
                    api.endpoints.cancelInputPortForDataProduct.initiate({ id: 'dp1', outputPortId: 'op1' }),
                ),
        ],
        [
            'revoking an Exploration Input Port',
            (store) =>
                store.dispatch(
                    api.endpoints.revokeInputPortForExploration.initiate({ id: 'ex1', outputPortId: 'op1' }),
                ),
        ],
        [
            'requesting a Data Product role',
            (store) =>
                store.dispatch(
                    api.endpoints.requestDataProductRoleAssignment.initiate({
                        user_id: 'u1',
                        role_id: 'r1',
                        data_product_id: 'dp1',
                    }),
                ),
        ],
        [
            'linking a Technical Asset to an Output Port',
            (store) =>
                store.dispatch(
                    api.endpoints.linkOutputPortToTechnicalAsset.initiate({
                        dataProductId: 'dp1',
                        outputPortId: 'op1',
                        linkTechnicalAssetToOutputPortRequest: { technical_asset_id: 'ta1' },
                    }),
                ),
        ],
    ])('refreshes my requests and pending actions after %s', async (_, mutate) => {
        const calls = { myRequests: 0, pendingActions: 0 };
        server.use(
            http.get('*/api/v2/users/current/my_requests', () => {
                calls.myRequests++;
                return HttpResponse.json({ my_requests: [] });
            }),
            http.get('*/api/v2/users/current/pending_actions', () => {
                calls.pendingActions++;
                return HttpResponse.json({ pending_actions: [] });
            }),
            http.post('*', () => HttpResponse.json(null)),
        );
        const store = createTestStore();
        store.dispatch(api.endpoints.getUserRequests.initiate(true));
        store.dispatch(api.endpoints.getUserPendingActions.initiate());
        await waitFor(() => expect(calls).toEqual({ myRequests: 1, pendingActions: 1 }));

        await mutate(store);

        await waitFor(() => expect(calls).toEqual({ myRequests: 2, pendingActions: 2 }));
    });
});
