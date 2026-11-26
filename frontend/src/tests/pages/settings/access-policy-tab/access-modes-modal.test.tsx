import { HttpResponse, http } from 'msw';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import AccessModesModal from '@/pages/settings/components/settings-tabs/access-policy-tab/access-modes-modal.tsx';
import type { AccessModeWithType } from '@/store/api/services/generated/configurationAccessModesApi.ts';
import { mockAccessModesHttp } from '@/tests/mocks/configurationAccessModes.ts';
import { mockGetPlugins } from '@/tests/mocks/plugins.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

const mockOnClose = vi.fn();

describe('AccessModesModal', () => {
    beforeEach(() => {
        mockGetPlugins();
        mockAccessModesHttp();
        mockOnClose.mockClear();
    });

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

        it('requires Name, Technical asset types and Description fields', async () => {
            const user = userEvent.setup();
            renderWithProviders(<AccessModesModal onClose={mockOnClose} />);

            const okButton = screen.getByRole('button', { name: /OK/i });
            await user.click(okButton);

            await waitFor(() => {
                expect(screen.getByText(/Please provide the name of the access mode/i)).toBeInTheDocument();
                expect(
                    screen.getByText(/Please provide at least one Technical Asset type for the access mode/i),
                ).toBeInTheDocument();
                expect(screen.getByText(/Please provide the description of the access mode/i)).toBeInTheDocument();
            });
        });

        it('only allows choosing a default for included Technical Asset types', async () => {
            const user = userEvent.setup();
            renderWithProviders(<AccessModesModal onClose={mockOnClose} />);

            const defaultForS3 = await screen.findByLabelText('Default for S3');
            expect(defaultForS3).toBeDisabled();

            await user.click(screen.getByLabelText('Include S3'));

            expect(defaultForS3).toBeEnabled();
            expect(defaultForS3).not.toBeChecked();
        });

        it('makes the access mode the default for an included type without a default', async () => {
            const user = userEvent.setup();
            renderWithProviders(<AccessModesModal onClose={mockOnClose} />);

            await user.click(await screen.findByLabelText('Include GitHub'));

            const defaultForGitHub = screen.getByLabelText('Default for GitHub');
            expect(defaultForGitHub).toBeChecked();
            expect(defaultForGitHub).toBeDisabled();

            await user.hover(defaultForGitHub.closest('label') ?? defaultForGitHub);
            expect(
                await screen.findByText(
                    "This is the default access mode for this type and can't be removed. Making another access mode the default replaces it.",
                ),
            ).toBeInTheDocument();
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
                    expect(body).toStrictEqual({
                        name: 'Write Access',
                        description: 'Write access to data',
                        technical_asset_types: ['S3TechnicalAssetConfiguration'],
                        default_for_technical_asset_types: ['S3TechnicalAssetConfiguration'],
                    });
                    return HttpResponse.json(body);
                }),
            );

            renderWithProviders(<AccessModesModal onClose={mockOnClose} />);

            await user.type(screen.getByPlaceholderText('Name'), 'Write Access');
            await user.click(await screen.findByLabelText('Include S3'));
            await user.click(screen.getByLabelText('Default for S3'));
            await user.type(screen.getByLabelText(/Description/i), 'Write access to data');

            const okButton = screen.getByRole('button', { name: /OK/i });
            await user.click(okButton);

            await waitFor(() => {
                expect(createCalled).toBe(true);
                expect(mockOnClose).toHaveBeenCalled();
            });
        });
    });

    describe('Edit Mode', () => {
        const mockAccessMode: AccessModeWithType = {
            id: '1',
            name: 'Read Only',
            technical_asset_types: ['S3TechnicalAssetConfiguration'],
            default_for_technical_asset_types: ['S3TechnicalAssetConfiguration'],
            in_use_technical_asset_types: [],
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

        it('cannot remove a type it is the default for while other access modes have that type', async () => {
            renderWithProviders(<AccessModesModal onClose={mockOnClose} editAccessMode={mockAccessMode} />);

            await waitFor(() => expect(screen.getByLabelText('Include S3')).toBeDisabled());
            expect(screen.getByLabelText('Include S3')).toBeChecked();
            expect(screen.getByLabelText('Default for S3')).toBeChecked();
        });

        it('cannot remove a type that is still in use', async () => {
            const user = userEvent.setup();
            renderWithProviders(
                <AccessModesModal
                    onClose={mockOnClose}
                    editAccessMode={{
                        ...mockAccessMode,
                        technical_asset_types: ['S3TechnicalAssetConfiguration', 'GitHubPlugin'],
                        default_for_technical_asset_types: [],
                        in_use_technical_asset_types: ['GitHubPlugin'],
                    }}
                />,
            );

            const includeGitHub = await screen.findByLabelText('Include GitHub');
            expect(includeGitHub).toBeDisabled();
            expect(includeGitHub).toBeChecked();
            expect(screen.getByLabelText('Include S3')).toBeEnabled();

            await user.hover(includeGitHub.closest('label') ?? includeGitHub);
            expect(
                await screen.findByText('Technical Assets of this type still use this access mode'),
            ).toBeInTheDocument();
        });

        it('requires Description field in edit mode', async () => {
            const user = userEvent.setup();
            const accessModeWithoutDesc = { ...mockAccessMode, description: '' };
            renderWithProviders(<AccessModesModal onClose={mockOnClose} editAccessMode={accessModeWithoutDesc} />);

            const descInput = screen.getByLabelText(/Description/i) as HTMLTextAreaElement;
            await user.clear(descInput);

            const okButton = screen.getByRole('button', { name: /OK/i });
            await user.click(okButton);

            await waitFor(() => {
                expect(screen.getByText(/Please provide the description of the access mode/i)).toBeInTheDocument();
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
                    expect(await request.json()).toStrictEqual({
                        description: 'Updated description',
                        technical_asset_types: ['S3TechnicalAssetConfiguration'],
                        default_for_technical_asset_types: ['S3TechnicalAssetConfiguration'],
                    });
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
