import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import InternalExplorer from '@/components/explorer/internal-explorer.tsx';
import { NodeType } from '@/store/api/services/generated/dataProductsApi.ts';
import type { Graph } from '@/store/api/services/generated/graphApi.ts';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockGetPlugins } from '@/tests/mocks/plugins.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, waitFor } from '@/tests/test-utils.tsx';

const mockGraph: Graph = {
    nodes: [
        {
            id: 'dp-1',
            type: NodeType.DataProductNode,
            isMain: true,
            data: { id: 'dp-1', name: 'Test Product', description: 'A test data product' },
        },
    ],
    edges: [],
};

describe('Explorer', () => {
    it('renders graph nodes — catches layout crashes and blank-graph regressions', async () => {
        allowAllAuth();
        mockGetPlugins();
        server.use(http.get('*/api/v2/data_products/:id/graph', () => HttpResponse.json(mockGraph)));

        // Use InternalExplorer directly to avoid React.lazy + Suspense timing complexity.
        // The global ResizeObserverStub (setup.ts) never fires, which is fine —
        // React Flow renders node DOM elements before measuring the viewport.
        renderWithProviders(<InternalExplorer id="dp-1" type="dataproduct" />);

        // React Flow renders each node as a div with data-id matching the node id.
        // If the graph layout library (dagre) crashes or the component fails to mount,
        // this element never appears in the DOM.
        await waitFor(() => expect(document.querySelector('[data-id="dp-1"]')).toBeInTheDocument(), { timeout: 5000 });
    });
});
