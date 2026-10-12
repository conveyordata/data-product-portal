import { HttpResponse, http } from 'msw';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { CreateDomainModal } from '@/pages/settings/components/settings-tabs/components/domain-table/domain-form-modal.component.tsx';
import { DomainTable } from '@/pages/settings/components/settings-tabs/components/domain-table/domain-table.component.tsx';
import { EnvironmentTable } from '@/pages/settings/components/settings-tabs/components/environment-table/environment-table.component.tsx';
import { mock_domains, mockGetDomains } from '@/tests/mocks/configurationDomains.ts';
import { mockEnvironments, mockGetEnvironments } from '@/tests/mocks/configurationEnvironments.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

describe('Domain settings without environment scope', () => {
    beforeEach(() => {
        mockGetDomains();
        mockGetEnvironments();
    });

    it.each(['create', 'edit'] as const)('only sends Domain metadata when saving in %s mode', async (mode) => {
        const save = vi.fn();
        const fetchEnvironments = vi.fn(() => HttpResponse.json({ environments: mockEnvironments }));
        server.use(
            http.get('*/api/v2/configuration/environments', fetchEnvironments),
            http.post('*/api/v2/configuration/domains', async ({ request }) => {
                save(await request.json());
                return HttpResponse.json({ id: 'id-1' });
            }),
            http.put('*/api/v2/configuration/domains/id-1', async ({ request }) => {
                save(await request.json());
                return HttpResponse.json({ id: 'id-1' });
            }),
        );
        renderWithProviders(
            <CreateDomainModal
                isOpen
                onClose={vi.fn()}
                mode={mode}
                initial={mode === 'edit' ? mock_domains[0] : undefined}
            />,
        );
        expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
        expect(screen.queryByText('Environment Setting')).not.toBeInTheDocument();
        const name = screen.getByRole('textbox', { name: 'Name' });
        const description = screen.getByRole('textbox', { name: 'Description' });
        await userEvent.clear(name);
        await userEvent.type(name, 'Research');
        await userEvent.clear(description);
        await userEvent.type(description, 'Research domain');
        await userEvent.click(screen.getByRole('button', { name: mode === 'edit' ? 'Update' : 'Create' }));
        await waitFor(() => expect(save).toHaveBeenCalledWith({ name: 'Research', description: 'Research domain' }));
        expect(fetchEnvironments).not.toHaveBeenCalled();
    });

    it('has no environment column or environment lookup in the Domain table', async () => {
        const fetchEnvironments = vi.fn(() => HttpResponse.json({ environments: mockEnvironments }));
        server.use(http.get('*/api/v2/configuration/environments', fetchEnvironments));
        renderWithProviders(<DomainTable />);
        expect(await screen.findByText('Finance')).toBeInTheDocument();
        expect(screen.queryByRole('columnheader', { name: 'Environments' })).not.toBeInTheDocument();
        expect(fetchEnvironments).not.toHaveBeenCalled();
    });

    it('keeps the general Environment catalogue and global-default controls', async () => {
        renderWithProviders(<EnvironmentTable />);
        expect(await screen.findByText('Development')).toBeInTheDocument();
        expect(screen.getByRole('columnheader', { name: /Global/ })).toBeInTheDocument();
        expect(screen.getAllByRole('checkbox')).toHaveLength(mockEnvironments.length);
    });
});
