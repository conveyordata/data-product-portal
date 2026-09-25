import { HttpResponse, http } from 'msw';
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
                HttpResponse.json({ access_modes: [] }),
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
        await user.click(screen.getByRole('button', { name: 'Grant access' }));

        await waitFor(() =>
            expect(requestBody).toEqual({
                consuming_abstract_data_product_id: 'consumer-id',
                justification: 'Required for reporting',
            }),
        );
    });
});
