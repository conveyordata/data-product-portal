import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { AboutTab } from '@/pages/output-port/components/dataset-tabs/about-tab/about-tab.tsx';
import { editRichText } from '@/tests/components/rich-text/text-editor.helpers.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';

describe('Output Port AboutTab', () => {
    it('edits with the Output Port permission and saves to the Output Port', async () => {
        let savedBody: unknown;
        server.use(
            http.get('*/api/v2/data_products/dp1/output_ports/op1', () =>
                HttpResponse.json({ id: 'op1', about: '<p>Saved about</p>' }),
            ),
            http.get('*/api/v2/authz/access/:action', ({ params, request }) =>
                HttpResponse.json({
                    allowed:
                        params.action === String(AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES) &&
                        new URL(request.url).searchParams.get('resource') === 'op1',
                }),
            ),
            http.put('*/api/v2/data_products/dp1/output_ports/op1/about', async ({ request }) => {
                savedBody = await request.json();
                return HttpResponse.json(null);
            }),
        );
        const { container } = renderWithProviders(<AboutTab dataProductId="dp1" outputPortId="op1" />);

        await userEvent.click(await screen.findByRole('button', { name: 'Edit content' }));
        await editRichText(container, 'Edited about');
        await userEvent.click(screen.getByRole('button', { name: 'Save changes' }));

        await waitFor(() => expect(savedBody).toEqual({ about: '<p>Edited about</p>' }));
    });
});
