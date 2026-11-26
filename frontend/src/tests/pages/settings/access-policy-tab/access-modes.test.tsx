import { HttpResponse, http } from 'msw';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import AccessModes from '@/pages/settings/components/settings-tabs/access-policy-tab/access-modes.tsx';
import { mockAccessModes, mockAccessModesHttp } from '@/tests/mocks/configurationAccessModes.ts';
import { mockGetPlugins } from '@/tests/mocks/plugins.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';
import * as feedback from '@/utils/feedback.ts';

describe('AccessModes', () => {
    const removeButtons = () => screen.getAllByText('Remove').map((label) => label.closest('button'));

    const removeReadWriteAndConfirm = async (user: ReturnType<typeof userEvent.setup>) => {
        await screen.findByText('Read Write');
        const readWriteRemove = removeButtons()[1];
        if (!readWriteRemove) throw new Error('Remove button not found');
        await user.click(readWriteRemove);
        await user.click(await screen.findByText('Confirm'));
    };

    beforeEach(() => {
        mockGetPlugins();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

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
        const user = userEvent.setup();
        mockAccessModesHttp();
        renderWithProviders(<AccessModes />);

        await waitFor(() => {
            expect(screen.getByRole('button', { name: /Add access mode/i })).toBeInTheDocument();
        });

        const addButton = screen.getByRole('button', { name: /Add access mode/i });
        await user.click(addButton);

        await waitFor(() => {
            expect(screen.getByText('Create Access Mode')).toBeInTheDocument();
        });
    });

    it('opens modal in edit mode when Edit button is clicked', async () => {
        const user = userEvent.setup();
        mockAccessModesHttp();
        renderWithProviders(<AccessModes />);

        await waitFor(() => {
            expect(screen.getAllByRole('button', { name: /Edit/i }).length).toBeGreaterThan(0);
        });

        const editButtons = screen.getAllByRole('button', { name: /Edit/i });
        await user.click(editButtons[0]);

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

    it('deletes an access mode successfully and shows a success message', async () => {
        const user = userEvent.setup();
        let deletedAccessModeId: string | undefined;
        const dispatchMessageSpy = vi.spyOn(feedback, 'dispatchMessage');

        server.use(
            http.delete('*/api/v2/configuration/access_modes/:id', ({ params }) => {
                deletedAccessModeId = String(params.id);
                return new HttpResponse(null, { status: 200 });
            }),
        );

        mockAccessModesHttp();
        renderWithProviders(<AccessModes />);

        await removeReadWriteAndConfirm(user);

        await waitFor(() => {
            expect(deletedAccessModeId).toBe('2');
            expect(dispatchMessageSpy).toHaveBeenCalledWith({
                content: 'Access mode deleted successfully',
                type: 'success',
            });
        });
    });

    it('disables Remove with an explanation when Technical Assets use it', async () => {
        const user = userEvent.setup({ pointerEventsCheck: 0 });
        mockAccessModesHttp([
            mockAccessModes[0],
            { ...mockAccessModes[1], in_use_technical_asset_types: ['S3TechnicalAssetConfiguration'] },
        ]);
        renderWithProviders(<AccessModes />);

        await screen.findByText('Read Write');
        const readWriteRemove = removeButtons()[1];
        expect(readWriteRemove).toBeDisabled();

        await user.hover(readWriteRemove ?? document.body);
        expect(await screen.findByText('Technical Assets use this access mode')).toBeInTheDocument();
    });

    it('disables Remove for the default of a type that has other access modes', async () => {
        const user = userEvent.setup({ pointerEventsCheck: 0 });
        mockAccessModesHttp();
        renderWithProviders(<AccessModes />);

        await screen.findByText('Read Only');
        const readOnlyRemove = removeButtons()[0];
        expect(readOnlyRemove).toBeDisabled();
        expect(removeButtons()[1]).toBeEnabled();

        await user.hover(readOnlyRemove ?? document.body);
        expect(await screen.findByText('Make another access mode the default for S3 first')).toBeInTheDocument();
    });
});
