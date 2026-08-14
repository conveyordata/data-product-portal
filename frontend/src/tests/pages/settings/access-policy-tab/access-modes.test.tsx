import { HttpResponse, http } from 'msw';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import AccessModes from '@/pages/settings/components/settings-tabs/access-policy-tab/access-modes.tsx';
import { CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR } from '@/store/common/api-errors.ts';
import * as errors from '@/store/common/errors.ts';
import { mockAccessModesHttp } from '@/tests/mocks/configurationAccessModes.ts';
import { mockGetPlugins } from '@/tests/mocks/plugins.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';
import * as feedback from '@/utils/feedback.ts';

describe('AccessModes', () => {
    const removeFirstAccessModeAndConfirm = async (user: ReturnType<typeof userEvent.setup>) => {
        await waitFor(() => {
            expect(screen.getAllByRole('button', { name: /Remove/i }).length).toBeGreaterThan(0);
        });

        await user.click(screen.getAllByRole('button', { name: /Remove/i })[0]);
        await user.click(await screen.findByRole('button', { name: /Confirm/i }));
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
            expect(screen.getByText('Access modes')).toBeInTheDocument();
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

        await removeFirstAccessModeAndConfirm(user);

        await waitFor(() => {
            expect(deletedAccessModeId).toBe('1');
            expect(dispatchMessageSpy).toHaveBeenCalledWith({
                content: 'Access mode deleted successfully',
                type: 'success',
            });
        });
    });

    it('shows expected error message when deleting an access mode in use fails', async () => {
        const user = userEvent.setup();
        const dispatchMessageSpy = vi.spyOn(feedback, 'dispatchMessage');

        server.use(
            http.delete('*/api/v2/configuration/access_modes/:id', () =>
                HttpResponse.json({ detail: CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR }, { status: 400 }),
            ),
        );

        mockAccessModesHttp();
        renderWithProviders(<AccessModes />);

        await removeFirstAccessModeAndConfirm(user);

        await waitFor(() => {
            expect(dispatchMessageSpy).toHaveBeenCalledWith({
                content: CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR,
                type: 'error',
            });
        });
    });

    it('shows generic error handling when deleting an access mode fails unexpectedly', async () => {
        const user = userEvent.setup();
        const showGenericErrorMessageSpy = vi.spyOn(errors, 'showGenericErrorMessage');

        server.use(
            http.delete('*/api/v2/configuration/access_modes/:id', () =>
                HttpResponse.json({ detail: 'Unexpected failure while deleting access mode' }, { status: 500 }),
            ),
        );

        mockAccessModesHttp();
        renderWithProviders(<AccessModes />);

        await removeFirstAccessModeAndConfirm(user);

        await waitFor(() => {
            expect(showGenericErrorMessageSpy).toHaveBeenCalledTimes(1);
        });
    });
});
