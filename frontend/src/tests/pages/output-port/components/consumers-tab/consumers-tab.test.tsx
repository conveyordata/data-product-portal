import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import {
    ConsumersTab,
    hasAccessOrPendingRequest,
} from '@/pages/output-port/components/dataset-tabs/consumers-tab/consumers-tab.tsx';
import {
    InputPortStatus,
    type OutputPortInputPort,
    RenewalStatus,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { mockExpiringSoonThreshold } from '@/tests/mocks/configurationAccessDurations.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockUserPendingActions } from '@/tests/mocks/userPendingActions.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

describe('ConsumersTab', () => {
    it.each([
        [true, true],
        [false, false],
    ])('shows the add action when access is %s', async (allowed, visible) => {
        mockExpiringSoonThreshold();
        mockUserPendingActions([]);
        server.use(
            http.get('*/api/v2/authz/access/:action', () => HttpResponse.json({ allowed })),
            http.get('*/api/v2/data_products/:dataProductId/output_ports/:outputPortId/input_ports/', () =>
                HttpResponse.json({ input_ports: [] }),
            ),
        );

        renderWithProviders(<ConsumersTab dataProductId="data-product-id" outputPortId="output-port-id" />);

        if (visible) {
            expect(await screen.findByText('Add consumer')).toBeInTheDocument();
        } else {
            expect(screen.queryByText('Add consumer')).not.toBeInTheDocument();
        }
    });

    it.each([
        ['active grant', InputPortStatus.Approved, null, null, true],
        ['lapsed grant not yet recomputed', InputPortStatus.Approved, '2000-01-01', null, false],
        ['pending request', InputPortStatus.Pending, null, null, true],
        ['pending renewal', InputPortStatus.Expired, '2000-01-01', RenewalStatus.Pending, true],
        ['revoked access', InputPortStatus.Revoked, null, null, false],
    ])('treats a link with %s as in use: %s', (_label, status, validUntil, renewalStatus, expected) => {
        const inputPort = {
            status,
            renewal_status: renewalStatus,
            current_request: { valid_until: validUntil },
        } as OutputPortInputPort;

        expect(hasAccessOrPendingRequest(inputPort)).toBe(expected);
    });
});
