import { describe, expect, it, vi } from 'vitest';
import SelectAccessModeModal from '@/pages/marketplace/output-port-marketplace-card/select-access-mode-modal.component.tsx';
import type { SearchOutputPortsResponseItem } from '@/store/api/services/generated/outputPortsSearchApi.ts';
import { mockOutputPorts } from '@/tests/mocks/outputPortsSearch.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

const outputPort: SearchOutputPortsResponseItem = {
    ...mockOutputPorts[0],
    access_modes: [
        {
            id: 'access-mode-1',
            name: 'Read',
            description: 'Read access',
        },
    ],
};

describe('SelectAccessModeModal', () => {
    it('submits selected access mode', async () => {
        const onClose = vi.fn();
        const selectAccessMode = vi.fn();
        const user = userEvent.setup();

        renderWithProviders(
            <SelectAccessModeModal outputPort={outputPort} onClose={onClose} selectAccessMode={selectAccessMode} />,
        );

        await user.click(screen.getByRole('radio'));
        await user.click(screen.getByRole('button', { name: /ok/i }));

        await waitFor(() => {
            expect(selectAccessMode).toHaveBeenCalledWith(outputPort.access_modes[0]);
        });
    });

    it('does not submit when no access mode is selected', async () => {
        const onClose = vi.fn();
        const selectAccessMode = vi.fn();
        const user = userEvent.setup();

        renderWithProviders(
            <SelectAccessModeModal outputPort={outputPort} onClose={onClose} selectAccessMode={selectAccessMode} />,
        );

        await user.click(screen.getByRole('button', { name: /ok/i }));

        await waitFor(() => {
            expect(screen.getByText('Please select an access mode')).toBeInTheDocument();
        });
        expect(selectAccessMode).not.toHaveBeenCalled();
    });
});
