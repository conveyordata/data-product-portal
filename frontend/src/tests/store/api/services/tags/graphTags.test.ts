import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { api } from '@/store/api/services/generated/completeServiceApi.ts';
import type { CreateTechnicalAssetRequest } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { type Node, NodeType } from '@/store/api/services/generated/graphApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { createTestStore, waitFor } from '@/tests/test-utils.tsx';

const node = (type: NodeType, entityId: string, nodeId = entityId): Node => ({
    id: nodeId,
    type,
    data: { id: entityId, name: entityId },
});

function setUpGraphs() {
    const calls = { global: 0, dp1: 0, dp3: 0 };
    const graph = (key: keyof typeof calls, nodes: Node[]) => () => {
        calls[key]++;
        return HttpResponse.json({ nodes, edges: [] });
    };
    server.use(
        http.get(
            '*/api/v2/graph',
            graph('global', [node(NodeType.DataProductNode, 'dp2'), node(NodeType.OutputPortNode, 'op1')]),
        ),
        http.get(
            '*/api/v2/data_products/dp1/graph',
            graph('dp1', [
                node(NodeType.DataProductNode, 'dp1'),
                node(NodeType.OutputPortNode, 'op1', 'input-port-1'),
                node(NodeType.TechnicalAssetNode, 'ta1'),
            ]),
        ),
        http.get(
            '*/api/v2/data_products/dp3/graph',
            graph('dp3', [node(NodeType.DataProductNode, 'dp3'), node(NodeType.TechnicalAssetNode, 'ta3')]),
        ),
        http.post('*/api/v2/data_products/dp2/output_ports/op1/input_ports/approve', () => HttpResponse.json(null)),
        http.put('*/api/v2/data_products/dp2/output_ports/op1/about', () => HttpResponse.json(null)),
        http.delete('*/api/v2/data_products/dp2/output_ports/op1', () => HttpResponse.json(null)),
        http.delete('*/api/v2/data_products/dp1', () => HttpResponse.json(null)),
    );

    const store = createTestStore();
    store.dispatch(api.endpoints.getGraphData.initiate({}));
    store.dispatch(api.endpoints.getDataProductGraphData.initiate({ id: 'dp1' }));
    store.dispatch(api.endpoints.getDataProductGraphData.initiate({ id: 'dp3' }));
    return { store, calls };
}

describe('graph tags', () => {
    it('refreshes the graphs involved when access is approved', async () => {
        const { store, calls } = setUpGraphs();
        await waitFor(() => expect(calls).toEqual({ global: 1, dp1: 1, dp3: 1 }));

        await store.dispatch(
            api.endpoints.approveOutputPortAsInputPort.initiate({
                dataProductId: 'dp2',
                outputPortId: 'op1',
                approveOutputPortAsInputPortRequest: { consuming_data_product_id: 'dp1' },
            }),
        );

        await waitFor(() => expect(calls).toEqual({ global: 2, dp1: 2, dp3: 1 }));
    });

    it('refreshes a graph that shows a changed Output Port of another Data Product', async () => {
        const { store, calls } = setUpGraphs();
        await waitFor(() => expect(calls).toEqual({ global: 1, dp1: 1, dp3: 1 }));

        await store.dispatch(
            api.endpoints.updateOutputPortAbout.initiate({
                dataProductId: 'dp2',
                id: 'op1',
                outputPortAboutUpdate: { about: '<p>Updated</p>' },
            }),
        );

        await waitFor(() => expect(calls.dp1).toBe(2));
        expect(calls).toEqual({ global: 2, dp1: 2, dp3: 1 });
    });

    it('refreshes only the global graph when an Output Port is deleted', async () => {
        const { store, calls } = setUpGraphs();
        await waitFor(() => expect(calls).toEqual({ global: 1, dp1: 1, dp3: 1 }));

        await store.dispatch(api.endpoints.removeOutputPort.initiate({ dataProductId: 'dp2', id: 'op1' }));

        await waitFor(() => expect(calls.global).toBe(2));
        expect(calls).toEqual({ global: 2, dp1: 1, dp3: 1 });
    });

    it('does not refetch the graph of a deleted Data Product', async () => {
        const { store, calls } = setUpGraphs();
        await waitFor(() => expect(calls).toEqual({ global: 1, dp1: 1, dp3: 1 }));

        await store.dispatch(api.endpoints.removeDataProduct.initiate('dp1'));

        await waitFor(() => expect(calls.global).toBe(2));
        expect(calls).toEqual({ global: 2, dp1: 1, dp3: 1 });
    });
});

describe('Output Port and Technical Asset graph tags', () => {
    function setUpEntityGraphs() {
        const calls = { outputPort: 0, technicalAsset: 0, exploration: 0 };
        const graph = (key: keyof typeof calls, nodes: Node[]) => () => {
            calls[key]++;
            return HttpResponse.json({ nodes, edges: [] });
        };
        server.use(
            http.get(
                '*/api/v2/data_products/dp2/output_ports/op1/graph',
                graph('outputPort', [node(NodeType.OutputPortNode, 'op1'), node(NodeType.DataProductNode, 'dp2')]),
            ),
            http.get(
                '*/api/v2/data_products/dp1/technical_assets/ta1/graph',
                graph('technicalAsset', [
                    node(NodeType.DataProductNode, 'dp1'),
                    node(NodeType.TechnicalAssetNode, 'ta1'),
                ]),
            ),
            http.get('*/api/v2/explorations/ex1', () => {
                calls.exploration++;
                return HttpResponse.json({ id: 'ex1' });
            }),
            http.post('*/api/v2/explorations', () => HttpResponse.json({ id: 'ex2' })),
            http.post('*/api/v2/data_products/dp1/technical_assets/', () => HttpResponse.json({ id: 'ta2' })),
            http.delete('*/api/v2/data_products/dp1/technical_assets/ta1', () => HttpResponse.json(null)),
            http.delete('*/api/v2/explorations/ex1', () => HttpResponse.json(null)),
        );

        const store = createTestStore();
        store.dispatch(api.endpoints.getOutputPortGraphData.initiate({ dataProductId: 'dp2', id: 'op1' }));
        store.dispatch(api.endpoints.getTechnicalAssetGraphData.initiate({ dataProductId: 'dp1', id: 'ta1' }));
        store.dispatch(api.endpoints.getExploration.initiate('ex1'));
        return { store, calls };
    }

    it('refreshes the graph of a requested Output Port when an Exploration is created with Input Ports', async () => {
        const { store, calls } = setUpEntityGraphs();
        await waitFor(() => expect(calls).toEqual({ outputPort: 1, technicalAsset: 1, exploration: 1 }));

        await store.dispatch(
            api.endpoints.createExploration.initiate({
                name: 'ex2',
                namespace: 'ex2',
                description: '',
                domain_id: 'd1',
                input_ports: { output_ports: [{ output_port_id: 'op1' }], justification: '' },
            }),
        );

        await waitFor(() => expect(calls.outputPort).toBe(2));
        expect(calls.technicalAsset).toBe(1);
    });

    it('refreshes the graph of a sibling Technical Asset when a Technical Asset is created', async () => {
        const { store, calls } = setUpEntityGraphs();
        await waitFor(() => expect(calls).toEqual({ outputPort: 1, technicalAsset: 1, exploration: 1 }));

        await store.dispatch(
            api.endpoints.createTechnicalAsset.initiate({
                dataProductId: 'dp1',
                createTechnicalAssetRequest: {} as CreateTechnicalAssetRequest,
            }),
        );

        await waitFor(() => expect(calls.technicalAsset).toBe(2));
        expect(calls.outputPort).toBe(1);
    });

    it('does not refetch the graph of a deleted Technical Asset', async () => {
        const { store, calls } = setUpEntityGraphs();
        await waitFor(() => expect(calls).toEqual({ outputPort: 1, technicalAsset: 1, exploration: 1 }));

        await store.dispatch(api.endpoints.removeTechnicalAsset.initiate({ dataProductId: 'dp1', id: 'ta1' }));
        await new Promise((resolve) => setTimeout(resolve, 100));

        expect(calls.technicalAsset).toBe(1);
    });

    it('does not refetch a deleted Exploration', async () => {
        const { store, calls } = setUpEntityGraphs();
        await waitFor(() => expect(calls).toEqual({ outputPort: 1, technicalAsset: 1, exploration: 1 }));

        await store.dispatch(api.endpoints.removeExploration.initiate('ex1'));
        await new Promise((resolve) => setTimeout(resolve, 100));

        expect(calls.exploration).toBe(1);
    });
});
