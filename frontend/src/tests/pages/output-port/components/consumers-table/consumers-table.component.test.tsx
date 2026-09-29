import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { ConsumersTable } from '@/pages/output-port/components/dataset-tabs/consumers-tab/components/consumers-table/consumers-table.component.tsx';
import {
    AbstractDataProductType,
    AccessDurationType,
    InputPortRequestDecision,
    InputPortStatus,
    type OutputPortInputPort,
    RenewalStatus,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

const requester = {
    id: 'user-1',
    email: 'john@example.com',
    external_id: 'john',
    first_name: 'John',
    last_name: 'Doe',
    has_seen_tour: true,
    can_become_admin: false,
};

function dateInDays(days: number): string {
    const date = new Date();
    date.setDate(date.getDate() + days);
    return date.toISOString().slice(0, 10);
}

function consumer(
    status: InputPortStatus,
    renewalStatus: RenewalStatus | null,
    validUntil: string | null,
): OutputPortInputPort {
    return {
        id: 'input-port-1',
        status,
        renewal_status: renewalStatus,
        consuming_abstract_data_product_id: 'consumer-1',
        consuming_abstract_data_product: {
            name: 'Consumer Product',
            namespace: 'consumer-product',
            abstract_data_product_type: AbstractDataProductType.DataProducts,
            is_redacted: false,
        },
        current_request: {
            id: 'request-1',
            justification: 'Because',
            valid_until: validUntil,
            access_duration_type: AccessDurationType.TimeBound,
            requested_by: requester,
            decision: InputPortRequestDecision.Approved,
            created_on: '2026-01-01T00:00:00',
            requested_on: '2026-01-01T00:00:00',
        },
    };
}

function mockApi() {
    server.use(
        http.get('*/api/v2/authz/access/:action', () => HttpResponse.json({ allowed: true })),
        http.get('*/api/v2/users/current/pending_actions', () => HttpResponse.json({ pending_actions: [] })),
        http.get('*/api/v2/configuration/access_durations/expiring_soon_threshold', () =>
            HttpResponse.json({ days: 14 }),
        ),
    );
}

function renderTable(link: OutputPortInputPort) {
    mockApi();
    renderWithProviders(<ConsumersTable dataProductId="dp-1" outputPortId="op-1" dataProducts={[link]} />, {
        routerProps: {},
    });
}

type Buttons = {
    renew: boolean;
    review: boolean;
    revoke: boolean;
};

describe('ConsumersTable', () => {
    it.each<[string, InputPortStatus, RenewalStatus | null, string | null, Buttons]>([
        [
            'Approved, far from expiry',
            InputPortStatus.Approved,
            null,
            dateInDays(365),
            { renew: false, review: false, revoke: true },
        ],
        [
            'Approved, expiring soon',
            InputPortStatus.Approved,
            null,
            dateInDays(5),
            { renew: true, review: false, revoke: true },
        ],
        [
            'Approved, renewal pending',
            InputPortStatus.Approved,
            RenewalStatus.Pending,
            dateInDays(5),
            { renew: false, review: true, revoke: true },
        ],
        [
            'Approved, renewal declined',
            InputPortStatus.Approved,
            RenewalStatus.Denied,
            dateInDays(365),
            { renew: true, review: false, revoke: true },
        ],
        ['Pending', InputPortStatus.Pending, null, null, { renew: false, review: true, revoke: false }],
        ['Revoked', InputPortStatus.Revoked, null, null, { renew: true, review: false, revoke: false }],
        ['Expired', InputPortStatus.Expired, null, dateInDays(-1), { renew: true, review: false, revoke: false }],
        ['Denied', InputPortStatus.Denied, null, null, { renew: true, review: false, revoke: false }],
        ['Cancelled', InputPortStatus.Cancelled, null, null, { renew: true, review: false, revoke: false }],
        [
            'Revoked, renewal pending',
            InputPortStatus.Revoked,
            RenewalStatus.Pending,
            null,
            { renew: false, review: true, revoke: false },
        ],
    ])('%s', async (_description, status, renewalStatus, validUntil, expected) => {
        renderTable(consumer(status, renewalStatus, validUntil));

        await screen.findByText('Consumer Product');
        await waitFor(() =>
            expect({
                renew: screen.queryByText('Renew Access') !== null,
                review: screen.queryByText('Review Access Request') !== null,
                revoke: screen.queryByText('Revoke Access') !== null,
            }).toEqual(expected),
        );
    });

    it('renews access for the consumer after confirmation', async () => {
        let body: unknown;
        server.use(
            http.post('*/api/v2/data_products/dp-1/output_ports/op-1/input_ports/renew', async ({ request }) => {
                body = await request.json();
                return HttpResponse.json(null);
            }),
        );
        renderTable(consumer(InputPortStatus.Revoked, null, null));

        const renewButton = await screen.findByRole('button', { name: 'Renew Access' });
        await waitFor(() => expect(renewButton).toBeEnabled());
        await userEvent.click(renewButton);
        await userEvent.click(await screen.findByRole('button', { name: 'Confirm' }));

        await waitFor(() => expect(body).toEqual({ consuming_data_product_id: 'consumer-1' }));
    });
});
