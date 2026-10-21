import { describe, expect, it } from 'vitest';
import { EnvironmentTable } from '@/pages/settings/components/settings-tabs/components/environment-table/environment-table.component.tsx';
import { mockEnvironments, mockGetEnvironments } from '@/tests/mocks/configurationEnvironments.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

describe('EnvironmentTable', () => {
    it('keeps the general Environment catalogue and global-default controls', async () => {
        mockGetEnvironments();
        renderWithProviders(<EnvironmentTable />);
        expect(await screen.findByText('Development')).toBeInTheDocument();
        expect(screen.getByRole('columnheader', { name: /Global/ })).toBeInTheDocument();
        expect(screen.getAllByRole('checkbox')).toHaveLength(mockEnvironments.length);
    });
});
