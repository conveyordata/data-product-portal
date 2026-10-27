import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { AboutTab } from '@/pages/data-product/components/data-product-tabs/about-tab/about-tab.tsx';
import { server } from '@/tests/mocks/server.ts';
import { editRichText, renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';

describe('Data Product AboutTab', () => {
    it('edits with the Data Product permission and saves to the Data Product', async () => {
        let savedBody: unknown;
        server.use(
            http.get('*/api/v2/data_products/dp1', () => HttpResponse.json({ id: 'dp1', about: '<p>Saved about</p>' })),
            http.get('*/api/v2/authz/access/:action', ({ params, request }) =>
                HttpResponse.json({
                    allowed:
                        params.action === String(AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES) &&
                        new URL(request.url).searchParams.get('resource') === 'dp1',
                }),
            ),
            http.put('*/api/v2/data_products/dp1/about', async ({ request }) => {
                savedBody = await request.json();
                return HttpResponse.json(null);
            }),
        );
        const { container } = renderWithProviders(<AboutTab dataProductId="dp1" />);

        await userEvent.click(await screen.findByRole('button', { name: 'Edit content' }));
        await editRichText(container, 'Edited about');
        await userEvent.click(screen.getByRole('button', { name: 'Save changes' }));

        await waitFor(() => expect(savedBody).toEqual({ about: '<p>Edited about</p>' }));
    });

    it('always shows the About of the selected Data Product, also when switching back to a cached one', async () => {
        server.use(
            http.get('*/api/v2/data_products/:id', ({ params }) =>
                HttpResponse.json({ id: params.id, about: `<p>About of ${params.id}</p>` }),
            ),
            http.get('*/api/v2/authz/access/:action', () => HttpResponse.json({ allowed: true })),
        );
        const { rerender } = renderWithProviders(<AboutTab dataProductId="dp1" />);
        expect(await screen.findByText('About of dp1')).toBeInTheDocument();

        rerender(<AboutTab dataProductId="dp2" />);
        expect(await screen.findByText('About of dp2')).toBeInTheDocument();
        expect(screen.queryByText('About of dp1')).not.toBeInTheDocument();

        rerender(<AboutTab dataProductId="dp1" />);
        expect(await screen.findByText('About of dp1')).toBeInTheDocument();
        expect(screen.queryByText('About of dp2')).not.toBeInTheDocument();
    });
});
