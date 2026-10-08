import { delay, HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { GrantOutputPortAccessModal } from '@/pages/output-port/components/dataset-tabs/consumers-tab/components/grant-output-port-access-modal.tsx';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

describe('GrantOutputPortAccessModal', () => {
    it('grants access to a selected data product', async () => {
        let requestBody: unknown;
        server.use(
            http.get('*/api/v2/data_products', () =>
                HttpResponse.json({
                    data_products: [
                        {
                            id: 'consumer-id',
                            name: 'Consumer',
                            description: 'Consumer description',
                            status: 'active',
                        },
                    ],
                }),
            ),
            http.get('*/api/v2/data_products/:dataProductId/output_ports/:outputPortId', () =>
                HttpResponse.json({ access_modes: [], access_type: { access_function: 'restricted' } }),
            ),
            http.post(
                '*/api/v2/data_products/:dataProductId/output_ports/:outputPortId/input_ports/grant',
                async ({ request }) => {
                    requestBody = await request.json();
                    return HttpResponse.json(null);
                },
            ),
        );
        const user = userEvent.setup();

        renderWithProviders(
            <GrantOutputPortAccessModal
                dataProductId="producer-id"
                outputPortId="output-port-id"
                existingConsumerIds={[]}
                onClose={() => undefined}
            />,
        );

        await user.click(await screen.findByRole('combobox'));
        await user.click(await screen.findByText('Consumer'));
        await user.type(screen.getByLabelText('Business justification'), 'Required for reporting');
        await user.click(screen.getByRole('button', { name: 'Grant Access' }));

        await waitFor(() =>
            expect(requestBody).toEqual({
                consuming_abstract_data_product_id: 'consumer-id',
                justification: 'Required for reporting',
            }),
        );
    });

    it('disables granting until the output port has loaded', async () => {
        server.use(
            http.get('*/api/v2/data_products', () => HttpResponse.json({ data_products: [] })),
            http.get('*/api/v2/data_products/:dataProductId/output_ports/:outputPortId', () => delay('infinite')),
        );

        renderWithProviders(
            <GrantOutputPortAccessModal
                dataProductId="producer-id"
                outputPortId="output-port-id"
                existingConsumerIds={[]}
                onClose={() => undefined}
            />,
        );

        expect(await screen.findByRole('button', { name: 'Grant Access' })).toBeDisabled();
        expect(screen.getByRole('radio', { name: 'Exploration' })).toBeDisabled();
    });

    it('lists explorations after switching the consumer type', async () => {
        server.use(
            http.get('*/api/v2/data_products', () => HttpResponse.json({ data_products: [] })),
            http.get('*/api/v2/explorations', () =>
                HttpResponse.json({
                    explorations: [{ id: 'exploration-id', name: 'My exploration', description: '', status: 'active' }],
                }),
            ),
            http.get('*/api/v2/data_products/:dataProductId/output_ports/:outputPortId', () =>
                HttpResponse.json({ access_modes: [], access_type: { access_function: 'restricted' } }),
            ),
        );
        const user = userEvent.setup();

        renderWithProviders(
            <GrantOutputPortAccessModal
                dataProductId="producer-id"
                outputPortId="output-port-id"
                existingConsumerIds={[]}
                onClose={() => undefined}
            />,
        );

        await user.click(await screen.findByText('Exploration'));
        await user.click(await screen.findByRole('combobox'));

        expect(await screen.findByText('My exploration')).toBeInTheDocument();
    });

    it('disables Explorations for Invite only Output Ports', async () => {
        server.use(
            http.get('*/api/v2/data_products', () => HttpResponse.json({ data_products: [] })),
            http.get('*/api/v2/data_products/:dataProductId/output_ports/:outputPortId', () =>
                HttpResponse.json({ access_modes: [], access_type: { access_function: 'private' } }),
            ),
        );

        renderWithProviders(
            <GrantOutputPortAccessModal
                dataProductId="producer-id"
                outputPortId="output-port-id"
                existingConsumerIds={[]}
                onClose={() => undefined}
            />,
        );

        await waitFor(() => expect(screen.getByRole('radio', { name: 'Exploration' })).toBeDisabled());
        expect(screen.getByRole('radio', { name: 'Data Product' })).toBeEnabled();
    });
});
