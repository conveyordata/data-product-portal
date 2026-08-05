import { describe, expect, it } from 'vitest';
import AccessModes from '@/pages/settings/components/settings-tabs/access-policy-tab/access-modes.tsx';
import { mockAccessModesHttp } from '@/tests/mocks/configurationAccessModes.ts';
import { renderWithProviders, screen, waitFor } from '@/tests/test-utils.tsx';

describe('AccessModes', () => {
    it('renders the access modes table with data', async () => {
        mockAccessModesHttp();
        renderWithProviders(<AccessModes />);

        await waitFor(() => {
            expect(screen.getByText('Access Modes')).toBeInTheDocument();
            expect(screen.getByText('Read Only')).toBeInTheDocument();
            expect(screen.getByText('Read Write')).toBeInTheDocument();
            expect(screen.getByText('Read-only access to data')).toBeInTheDocument();
            expect(screen.getByText('Read and write access to data')).toBeInTheDocument();
        });
    });

    it('renders the Add access mode button', async () => {
        mockAccessModesHttp();
        renderWithProviders(<AccessModes />);

        await waitFor(() => {
            expect(screen.getByRole('button', { name: /Add access mode/i })).toBeInTheDocument();
        });
    });

    it('opens modal in create mode when Add access mode button is clicked', async () => {
        mockAccessModesHttp();
        renderWithProviders(<AccessModes />);

        await waitFor(() => {
            expect(screen.getByRole('button', { name: /Add access mode/i })).toBeInTheDocument();
        });

        const addButton = screen.getByRole('button', { name: /Add access mode/i });
        addButton.click();

        await waitFor(() => {
            expect(screen.getByText('Create Access Mode')).toBeInTheDocument();
        });
    });

    it('opens modal in edit mode when Edit button is clicked', async () => {
        mockAccessModesHttp();
        renderWithProviders(<AccessModes />);

        await waitFor(() => {
            expect(screen.getAllByRole('button', { name: /Edit/i }).length).toBeGreaterThan(0);
        });

        const editButtons = screen.getAllByRole('button', { name: /Edit/i });
        editButtons[0].click();

        await waitFor(() => {
            expect(screen.getByText('Edit Access Mode')).toBeInTheDocument();
        });
    });

    it('renders Edit button for each access mode', async () => {
        mockAccessModesHttp();
        renderWithProviders(<AccessModes />);

        await waitFor(() => {
            const editButtons = screen.getAllByRole('button', { name: /Edit/i });
            expect(editButtons).toHaveLength(2);
        });
    });
});
