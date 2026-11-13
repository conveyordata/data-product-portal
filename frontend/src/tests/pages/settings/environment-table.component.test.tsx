import { HttpResponse, http } from 'msw';
import { describe, expect, it, vi } from 'vitest';
import { EnvironmentTable } from '@/pages/settings/components/settings-tabs/components/environment-table/environment-table.component.tsx';
import { mockEnvironments, mockGetEnvironments } from '@/tests/mocks/configurationEnvironments.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent } from '@/tests/test-utils.tsx';

describe('EnvironmentTable', () => {
    it('keeps the general Environment catalogue and global-default controls', async () => {
        mockGetEnvironments();
        renderWithProviders(<EnvironmentTable />);
        expect(await screen.findByText('Development')).toBeInTheDocument();
        expect(screen.getByRole('columnheader', { name: /Global/ })).toBeInTheDocument();
        expect(screen.getAllByRole('checkbox')).toHaveLength(mockEnvironments.length);
    });

    it('lists environments by their order with unset orders last', async () => {
        mockGetEnvironments([
            { ...mockEnvironments[0], position: null },
            { ...mockEnvironments[1], position: 1 },
            { ...mockEnvironments[2], position: 2 },
        ]);
        renderWithProviders(<EnvironmentTable />);
        await screen.findByText('Production');
        const names = screen
            .getAllByRole('row')
            .slice(1)
            .map((row) => row.textContent);
        expect(names[0]).toContain('Production');
        expect(names[1]).toContain('Test');
        expect(names[2]).toContain('Development');
    });

    it('saves the order of an environment', async () => {
        mockGetEnvironments();
        let body: unknown;
        server.use(
            http.patch('*/api/v2/configuration/environments/env-dev', async ({ request }) => {
                body = await request.json();
                return HttpResponse.json({ ...mockEnvironments[0], position: 3 });
            }),
        );
        renderWithProviders(<EnvironmentTable />);
        const input = await screen.findByLabelText('Order of Development');
        await userEvent.type(input, '3');
        await userEvent.tab();
        await vi.waitFor(() => expect(body).toEqual({ position: 3 }));
    });
});
