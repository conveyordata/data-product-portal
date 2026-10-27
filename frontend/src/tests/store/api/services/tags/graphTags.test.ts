import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { api } from '@/store/api/services/generated/completeServiceApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { createTestStore, waitFor } from '@/tests/test-utils.tsx';

function setUpGraphs() {
    const calls = { global: 0, dataProduct: 0 };
    server.use(
        http.get('*/api/v2/graph', () => {
            calls.global++;
            return HttpResponse.json({ nodes: [], edges: [] });
        }),
        http.get('*/api/v2/data_products/dp1/graph', () => {
            calls.dataProduct++;
            return HttpResponse.json({ nodes: [], edges: [] });
        }),
        http.post('*/api/v2/data_products/dp2/output_ports/op1/input_ports/approve', () => HttpResponse.json(null)),
        http.delete('*/api/v2/data_products/dp2/output_ports/op1', () => HttpResponse.json(null)),
    );

    const store = createTestStore();
    store.dispatch(api.endpoints.getGraphData.initiate({}));
    store.dispatch(api.endpoints.getDataProductGraphData.initiate({ id: 'dp1' }));
    return { store, calls };
}

describe('graph tag invalidation', () => {
    it('refreshes every explorer graph when access is approved', async () => {
        const { store, calls } = setUpGraphs();
        await waitFor(() => expect(calls).toEqual({ global: 1, dataProduct: 1 }));

        await store.dispatch(
            api.endpoints.approveOutputPortAsInputPort.initiate({
                dataProductId: 'dp2',
                outputPortId: 'op1',
                approveOutputPortAsInputPortRequest: { consuming_data_product_id: 'dp1' },
            }),
        );

        await waitFor(() => expect(calls).toEqual({ global: 2, dataProduct: 2 }));
    });

    it('refreshes only the global explorer when an output port is deleted', async () => {
        const { store, calls } = setUpGraphs();
        await waitFor(() => expect(calls).toEqual({ global: 1, dataProduct: 1 }));

        await store.dispatch(api.endpoints.removeOutputPort.initiate({ dataProductId: 'dp2', id: 'op1' }));

        await waitFor(() => expect(calls.global).toBe(2));
        expect(calls.dataProduct).toBe(1);
    });
});
