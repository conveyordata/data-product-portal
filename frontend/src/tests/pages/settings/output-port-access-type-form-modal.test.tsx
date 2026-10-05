import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { OutputPortAccessTypeFormModal } from '@/pages/settings/components/settings-tabs/components/output-port-access-types-table/output-port-access-type-form-modal.component.tsx';
import {
    OutputPortAccessFunction,
    type OutputPortAccessTypesGetItem,
} from '@/store/api/services/generated/configurationOutputPortAccessTypesApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, waitFor } from '@/tests/test-utils.tsx';

const mockOnClose = vi.fn();

const accessType: OutputPortAccessTypesGetItem = {
    id: 'access-type-1',
    name: 'Confidential',
    description: '',
    access_function: OutputPortAccessFunction.Restricted,
    output_port_count: 3,
};

describe('OutputPortAccessTypeFormModal function change confirmation', () => {
    let updateBody: unknown;

    beforeEach(() => {
        mockOnClose.mockClear();
        updateBody = undefined;
        server.use(
            http.put('*/api/v2/configuration/output_port_access_types/:id', async ({ request }) => {
                updateBody = await request.json();
                return HttpResponse.json(accessType);
            }),
        );
    });

    const changeFunctionTo = async (user: ReturnType<typeof userEvent.setup>, title: string) => {
        await user.click(screen.getByRole('combobox'));
        await user.click(await screen.findByTitle(title));
        await user.click(screen.getByRole('button', { name: 'Update' }));
    };

    it('explains the impact and saves after confirming', async () => {
        const user = userEvent.setup();
        renderWithProviders(
            <OutputPortAccessTypeFormModal onClose={mockOnClose} initial={accessType} isLastInviteOnly={false} />,
        );

        await changeFunctionTo(user, 'Invite only (hidden)');

        expect((await screen.findAllByText('Confirm function change')).length).toBeGreaterThan(0);
        expect(
            screen.getByText(
                'This will affect 3 Output Ports, which will be hidden from everyone outside the owning team.',
            ),
        ).toBeInTheDocument();
        expect(updateBody).toBeUndefined();

        await user.click(screen.getByRole('button', { name: 'Confirm change' }));

        await waitFor(() => {
            expect(updateBody).toMatchObject({ access_function: OutputPortAccessFunction.Private });
            expect(mockOnClose).toHaveBeenCalled();
        });
    });

    it('does not save when the confirmation is cancelled', async () => {
        const user = userEvent.setup();
        renderWithProviders(
            <OutputPortAccessTypeFormModal onClose={mockOnClose} initial={accessType} isLastInviteOnly={false} />,
        );

        await changeFunctionTo(user, 'Invite only (hidden)');
        await screen.findAllByText('Confirm function change');
        // The confirmation renders after the edit modal, so its Cancel button comes last.
        const cancelButtons = screen.getAllByRole('button', { name: 'Cancel' });
        await user.click(cancelButtons[cancelButtons.length - 1]);

        expect(updateBody).toBeUndefined();
        expect(mockOnClose).not.toHaveBeenCalled();
    });

    it('saves without confirmation when only the name changes', async () => {
        const user = userEvent.setup();
        renderWithProviders(
            <OutputPortAccessTypeFormModal onClose={mockOnClose} initial={accessType} isLastInviteOnly={false} />,
        );

        await user.type(screen.getByLabelText('Name'), ' v2');
        await user.click(screen.getByRole('button', { name: 'Update' }));

        await waitFor(() => {
            expect(updateBody).toMatchObject({ name: 'Confidential v2' });
            expect(mockOnClose).toHaveBeenCalled();
        });
        expect(screen.queryAllByText('Confirm function change')).toHaveLength(0);
    });

    it('warns that hidden Output Ports become visible when leaving Invite only', async () => {
        const user = userEvent.setup();
        renderWithProviders(
            <OutputPortAccessTypeFormModal
                onClose={mockOnClose}
                initial={{ ...accessType, access_function: OutputPortAccessFunction.Private }}
                isLastInviteOnly={false}
            />,
        );

        await changeFunctionTo(user, 'Approval required');

        expect(
            await screen.findByText(
                'This will affect 3 Output Ports, which will become visible to the whole organisation.',
            ),
        ).toBeInTheDocument();
    });

    it('saves without confirmation when no Output Ports use the Access Type', async () => {
        const user = userEvent.setup();
        renderWithProviders(
            <OutputPortAccessTypeFormModal
                onClose={mockOnClose}
                initial={{ ...accessType, output_port_count: 0 }}
                isLastInviteOnly={false}
            />,
        );

        await changeFunctionTo(user, 'Invite only (hidden)');

        await waitFor(() => {
            expect(updateBody).toMatchObject({ access_function: OutputPortAccessFunction.Private });
            expect(mockOnClose).toHaveBeenCalled();
        });
        expect(screen.queryAllByText('Confirm function change')).toHaveLength(0);
    });
});
