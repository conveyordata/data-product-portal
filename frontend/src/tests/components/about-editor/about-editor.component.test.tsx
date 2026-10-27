import { afterEach, describe, expect, it, vi } from 'vitest';
import { AboutEditor, type AboutSource } from '@/components/about-editor/about-editor.component.tsx';
import { editRichText, renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';
import * as feedback from '@/utils/feedback.ts';

type Query = AboutSource['query'];

const loadedQuery = (about: string | null = '<p>Saved about</p>'): Query => ({
    currentData: { id: 'entity-1', about },
    isFetching: false,
    isUninitialized: false,
    isError: false,
    refetch: vi.fn(),
});

const source = (overrides: Partial<AboutSource> = {}): AboutSource => ({
    query: loadedQuery(),
    canEdit: true,
    isSaving: false,
    save: vi.fn().mockResolvedValue(undefined),
    ...overrides,
});

describe('AboutEditor', () => {
    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('shows a spinner while the About is loading', () => {
        const { container } = renderWithProviders(
            <AboutEditor source={source({ query: { ...loadedQuery(), currentData: undefined, isFetching: true } })} />,
        );

        expect(container.querySelector('.ant-spin')).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Edit content' })).not.toBeInTheDocument();
    });

    it('offers a retry when loading fails', async () => {
        const refetch = vi.fn();
        renderWithProviders(
            <AboutEditor
                source={source({ query: { ...loadedQuery(), currentData: undefined, isError: true, refetch } })}
            />,
        );

        await userEvent.click(screen.getByRole('button', { name: 'Try again' }));

        expect(screen.getByText("Couldn't load this section")).toBeInTheDocument();
        expect(refetch).toHaveBeenCalled();
    });

    it('is read-only without edit permission', async () => {
        renderWithProviders(<AboutEditor source={source({ canEdit: false })} />);

        expect(await screen.findByText('Saved about')).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Edit content' })).not.toBeInTheDocument();
    });

    it('saves the edited About, confirms it and leaves edit mode', async () => {
        const dispatchMessageSpy = vi.spyOn(feedback, 'dispatchMessage');
        const save = vi.fn().mockResolvedValue(undefined);
        const { container } = renderWithProviders(<AboutEditor source={source({ save })} />);

        await userEvent.click(await screen.findByRole('button', { name: 'Edit content' }));
        await editRichText(container, 'Edited about');
        await userEvent.click(screen.getByRole('button', { name: 'Save changes' }));

        expect(save).toHaveBeenCalledWith('<p>Edited about</p>');
        expect(await screen.findByRole('button', { name: 'Edit content' })).toBeInTheDocument();
        expect(dispatchMessageSpy).toHaveBeenCalledWith({
            content: 'About section successfully updated',
            type: 'success',
        });
    });

    it('reports a failed save and stays in edit mode', async () => {
        const dispatchMessageSpy = vi.spyOn(feedback, 'dispatchMessage');
        const { container } = renderWithProviders(
            <AboutEditor source={source({ save: vi.fn().mockRejectedValue(new Error('failed')) })} />,
        );

        await userEvent.click(await screen.findByRole('button', { name: 'Edit content' }));
        await editRichText(container, 'Edited about');
        await userEvent.click(screen.getByRole('button', { name: 'Save changes' }));

        await waitFor(() =>
            expect(dispatchMessageSpy).toHaveBeenCalledWith({
                content: 'Could not update about section',
                type: 'error',
            }),
        );
        expect(screen.getByRole('button', { name: 'Save changes' })).toBeInTheDocument();
    });
});
