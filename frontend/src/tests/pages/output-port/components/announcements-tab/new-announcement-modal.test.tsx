import { describe, expect, it, vi } from 'vitest';
import { NewAnnouncementModal } from '@/pages/output-port/components/dataset-tabs/announcements-tab/new-announcement-modal.tsx';
import { renderWithProviders, screen, userEvent } from '@/tests/test-utils.tsx';

describe('NewAnnouncementModal', () => {
    it('shows required errors and counts characters under the fields', async () => {
        renderWithProviders(
            <NewAnnouncementModal
                dataProductId="data-product-id"
                outputPortId="output-port-id"
                consumerCount={4}
                onClose={vi.fn()}
            />,
        );

        expect(screen.getByText('This will notify 4 Consuming Data Products.')).toBeInTheDocument();
        await userEvent.click(screen.getByRole('button', { name: 'Publish' }));

        expect(await screen.findByText('Please provide a title')).toBeInTheDocument();
        expect(screen.getByText('Please provide a message')).toBeInTheDocument();

        await userEvent.type(screen.getByPlaceholderText('e.g. Version 2 is now available'), 'New columns');
        expect(screen.getByText('11 / 100')).toBeInTheDocument();
    });
});
