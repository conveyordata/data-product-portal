import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { describe, expect, it, vi } from 'vitest';
import AccessModesModal from '@/pages/settings/components/settings-tabs/access-policy-tab/access-modes-modal.tsx';
import type { AccessMode } from '@/store/api/services/generated/configurationAccessModesApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, waitFor } from '@/tests/test-utils.tsx';

const mockOnClose = vi.fn();

describe('AccessModesModal', () => {
    describe('Create Mode', () => {
        it('renders with Create Access Mode title when editAccessMode is undefined', () => {
            renderWithProviders(<AccessModesModal onClose={mockOnClose} />);

            expect(screen.getByText('Create Access Mode')).toBeInTheDocument();
        });

        it('renders Name field as enabled in create mode', () => {
            renderWithProviders(<AccessModesModal onClose={mockOnClose} />);

            const nameInput = screen.getByPlaceholderText('Name') as HTMLInputElement;
            expect(nameInput).not.toBeDisabled();
        });

        it('renders required Description field in create mode', () => {
            renderWithProviders(<AccessModesModal onClose={mockOnClose} />);

            expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
        });

        it('requires both Name and Description fields', async () => {
            const user = userEvent.setup();
            renderWithProviders(<AccessModesModal onClose={mockOnClose} />);

            const okButton = screen.getByRole('button', { name: /OK/i });
            await user.click(okButton);

            await waitFor(() => {
                expect(screen.getByText(/Please input the name of the access mode/i)).toBeInTheDocument();
                expect(screen.getByText(/Please input the description of the access mode/i)).toBeInTheDocument();
            });
        });

        it('closes modal on cancel button click', async () => {
            const user = userEvent.setup();
            renderWithProviders(<AccessModesModal onClose={mockOnClose} />);

            const cancelButton = screen.getByRole('button', { name: /Cancel/i });
            await user.click(cancelButton);

            expect(mockOnClose).toHaveBeenCalled();
        });

        it('submits form with valid data and calls onClose', async () => {
            const user = userEvent.setup();
            let createCalled = false;

            server.use(
                http.post('*/api/v2/configuration/access_modes', async ({ request }) => {
                    createCalled = true;
                    const body = await request.json();
                    return HttpResponse.json(body);
                }),
            );

            renderWithProviders(<AccessModesModal onClose={mockOnClose} />);

            const nameInput = screen.getByPlaceholderText('Name');
            const descInput = screen.getByLabelText(/Description/i);

            await user.type(nameInput, 'Write Access');
            await user.type(descInput, 'Write access to data');

            const okButton = screen.getByRole('button', { name: /OK/i });
            await user.click(okButton);

            await waitFor(() => {
                expect(createCalled).toBe(true);
                expect(mockOnClose).toHaveBeenCalled();
            });
        });
    });

    describe('Edit Mode', () => {
        const mockAccessMode: AccessMode = {
            id: '1',
            name: 'Read Only',
            description: 'Read-only access to data',
        };

        it('renders with Edit Access Mode title when editAccessMode is provided', () => {
            renderWithProviders(<AccessModesModal onClose={mockOnClose} editAccessMode={mockAccessMode} />);

            expect(screen.getByText('Edit Access Mode')).toBeInTheDocument();
        });

        it('renders Name field as disabled in edit mode', () => {
            renderWithProviders(<AccessModesModal onClose={mockOnClose} editAccessMode={mockAccessMode} />);

            const nameInput = screen.getByPlaceholderText('Name') as HTMLInputElement;
            expect(nameInput).toBeDisabled();
        });

        it('pre-fills form with existing access mode data', () => {
            renderWithProviders(<AccessModesModal onClose={mockOnClose} editAccessMode={mockAccessMode} />);

            const nameInput = screen.getByPlaceholderText('Name') as HTMLInputElement;
            expect(nameInput.value).toBe('Read Only');
        });

        it('requires Description field in edit mode', async () => {
            const user = userEvent.setup();
            const accessModeWithoutDesc = { ...mockAccessMode, description: '' };
            renderWithProviders(<AccessModesModal onClose={mockOnClose} editAccessMode={accessModeWithoutDesc} />);

            const descInput = screen.getByDisplayValue('') as HTMLTextAreaElement;
            await user.clear(descInput);

            const okButton = screen.getByRole('button', { name: /OK/i });
            await user.click(okButton);

            await waitFor(() => {
                expect(screen.getByText(/Please input the description of the access mode/i)).toBeInTheDocument();
            });
        });

        it('closes modal on cancel button click in edit mode', async () => {
            const user = userEvent.setup();
            renderWithProviders(<AccessModesModal onClose={mockOnClose} editAccessMode={mockAccessMode} />);

            const cancelButton = screen.getByRole('button', { name: /Cancel/i });
            await user.click(cancelButton);

            expect(mockOnClose).toHaveBeenCalled();
        });

        it('submits form with updated description and calls onClose', async () => {
            const user = userEvent.setup();
            let updateCalled = false;

            server.use(
                http.put('*/api/v2/configuration/access_modes/:id', async ({ request }) => {
                    updateCalled = true;
                    expect(await request.json()).toStrictEqual({ description: 'Updated description' });
                    return HttpResponse.json(mockAccessMode);
                }),
            );

            renderWithProviders(<AccessModesModal onClose={mockOnClose} editAccessMode={mockAccessMode} />);

            const descInput = screen.getByLabelText(/Description/i);
            await user.clear(descInput);
            await user.type(descInput, 'Updated description');

            const okButton = screen.getByRole('button', { name: /OK/i });
            await user.click(okButton);

            await waitFor(() => {
                expect(updateCalled).toBe(true);
                expect(mockOnClose).toHaveBeenCalled();
            });
        });
    });
});
