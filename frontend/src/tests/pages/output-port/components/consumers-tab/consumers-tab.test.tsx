import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { ConsumersTab } from '@/pages/output-port/components/dataset-tabs/consumers-tab/consumers-tab.tsx';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

describe('ConsumersTab', () => {
    it.each([
        [true, true],
        [false, false],
    ])('shows the add action when access is %s', async (allowed, visible) => {
        server.use(
            http.get('*/api/v2/authz/access/:action', () => HttpResponse.json({ allowed })),
            http.get('*/api/v2/data_products/:dataProductId/output_ports/:outputPortId/input_ports/', () =>
                HttpResponse.json({ input_ports: [] }),
            ),
            http.get('*/api/v2/users/current/pending_actions', () => HttpResponse.json({ pending_actions: [] })),
        );

        renderWithProviders(<ConsumersTab dataProductId="data-product-id" outputPortId="output-port-id" />);

        if (visible) {
            expect(await screen.findByText('Add consumer')).toBeInTheDocument();
        } else {
            expect(screen.queryByText('Add consumer')).not.toBeInTheDocument();
        }
    });
});
