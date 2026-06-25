import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ReviewRequestModal } from '@/components/pending-access-requests-modal/review-request-modal.tsx';
import type { DataProductOutputPortPendingAction } from '@/store/api/services/generated/usersApi.ts';
import { fireEvent, renderWithProviders, screen, waitFor } from '@/tests/test-utils.tsx';

const mockInputPortAction: DataProductOutputPortPendingAction = {
    id: 'action-1',
    justification: 'We need this data for our quarterly reports.',
    consuming_abstract_data_product_id: 'adp-1',
    output_port_id: 'op-1',
    status: 'pending',
    requested_on: '2024-03-15T10:00:00Z',
    output_port: {
        id: 'op-1',
        name: 'Sales Output Port',
        namespace: 'sales',
        description: 'Sales data output port',
        status: 'active',
        access_type: 'restricted',
        data_product_id: 'dp-1',
        tags: [],
    },
    consuming_abstract_data_product: {
        name: 'Marketing Analytics',
        namespace: 'marketing',
        abstract_data_product_type: 'data_products',
    },
    requested_by: {
        id: 'user-1',
        email: 'alice@example.com',
        external_id: 'ext-1',
        first_name: 'Alice',
        last_name: 'Smith',
        has_seen_tour: true,
        can_become_admin: false,
    },
    denied_by: null,
    approved_by: null,
    pending_action_type: 'InputPort',
};

function renderModal(props: Partial<Parameters<typeof ReviewRequestModal>[0]> = {}) {
    const defaults = {
        action: mockInputPortAction,
        open: true,
        onClose: vi.fn(),
        onAccept: vi.fn(),
        onReject: vi.fn(),
    };
    return renderWithProviders(<ReviewRequestModal {...defaults} {...props} />);
}

describe('ReviewRequestModal — InputPort', () => {
    it('calls onAccept with the action when Accept is clicked (no reasoning required)', async () => {
        const onClose = vi.fn();
        const onAccept = vi.fn();
        renderModal({ onAccept, onClose });
        fireEvent.click(screen.getByRole('button', { name: /accept/i }));
        expect(onAccept).toHaveBeenCalledWith(mockInputPortAction, undefined);
        expect(onClose).toHaveBeenCalled();
    });

    it('Passes reasoning on accept when filled in', async () => {
        const onClose = vi.fn();
        const onAccept = vi.fn();
        renderModal({ onAccept, onClose });

        const textarea = screen.getByRole('textbox');
        const reasoning = 'Approved because you are awesome.';
        await userEvent.type(textarea, reasoning);
        fireEvent.click(screen.getByRole('button', { name: /accept/i }));
        expect(onAccept).toHaveBeenCalledWith(mockInputPortAction, reasoning);
        expect(onClose).toHaveBeenCalled();
    });

    it('shows validation error when declining without reasoning', async () => {
        const onReject = vi.fn();
        renderModal({ onReject });
        fireEvent.click(screen.getByRole('button', { name: /decline/i }));
        await waitFor(() => {
            expect(screen.getByText('A reasoning is required when declining')).toBeInTheDocument();
        });
        expect(onReject).not.toHaveBeenCalled();
    });

    it('calls onReject with action and reasoning when Decline is clicked with reasoning filled in', async () => {
        const onClose = vi.fn();

        const onReject = vi.fn();
        renderModal({ onReject, onClose });
        const textarea = screen.getByRole('textbox');
        await userEvent.type(textarea, 'Not approved due to policy.');
        fireEvent.click(screen.getByRole('button', { name: /decline/i }));
        await waitFor(() => {
            expect(onReject).toHaveBeenCalledWith(mockInputPortAction, 'Not approved due to policy.');
        });
        expect(onClose).toHaveBeenCalled();
    });
});
