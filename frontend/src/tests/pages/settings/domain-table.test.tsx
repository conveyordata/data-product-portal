import { HttpResponse, http } from 'msw';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { DomainTable } from '@/pages/settings/components/settings-tabs/components/domain-table/domain-table.component.tsx';
import { mock_domains, mockGetDomains } from '@/tests/mocks/configurationDomains.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';
import * as feedback from '@/utils/feedback.ts';

describe('DomainTable', () => {
    afterEach(() => {
        vi.restoreAllMocks();
    });

    const removeDomain = async (deleteStatus: number) => {
        mockGetDomains([{ ...mock_domains[0], abstract_data_product_count: 0 }]);
        server.use(
            http.get('*/api/v2/configuration/environments', () => HttpResponse.json({ environments: [] })),
            http.delete('*/api/v2/configuration/domains/:id', () => new HttpResponse(null, { status: deleteStatus })),
        );
        const dispatchMessageSpy = vi.spyOn(feedback, 'dispatchMessage');
        const user = userEvent.setup();
        renderWithProviders(<DomainTable />);

        await user.click(await screen.findByRole('button', { name: /Remove/i }));
        await user.click(await screen.findByRole('button', { name: /Confirm/i }));
        return dispatchMessageSpy;
    };

    it('reports a pending deletion when the domain waits for finalizers', async () => {
        const dispatchMessageSpy = await removeDomain(202);

        await waitFor(() => {
            expect(dispatchMessageSpy).toHaveBeenCalledWith(expect.objectContaining({ type: 'info' }));
        });
    });

    it('reports a removed domain when it is deleted immediately', async () => {
        const dispatchMessageSpy = await removeDomain(200);

        await waitFor(() => {
            expect(dispatchMessageSpy).toHaveBeenCalledWith(expect.objectContaining({ type: 'success' }));
        });
    });
});
