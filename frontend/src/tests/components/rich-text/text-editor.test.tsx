import { describe, expect, it, vi } from 'vitest';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor.tsx';
import { editRichText, renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

const saved = '<p>Saved about</p>';
const edited = '<p>Edited about</p>';

describe('TextEditor', () => {
    it('only allows saving once the content changed', async () => {
        renderWithProviders(<TextEditor initialContent={saved} onSubmit={vi.fn()} />);

        await userEvent.click(await screen.findByRole('button', { name: 'Edit content' }));

        expect(screen.getByRole('button', { name: 'Save changes' })).toBeDisabled();
    });

    it('saves the edited content and leaves edit mode once the save succeeds', async () => {
        const onSubmit = vi.fn().mockResolvedValue(undefined);
        const { container } = renderWithProviders(<TextEditor initialContent={saved} onSubmit={onSubmit} />);

        await userEvent.click(await screen.findByRole('button', { name: 'Edit content' }));
        await editRichText(container, 'Edited about');
        await userEvent.click(screen.getByRole('button', { name: 'Save changes' }));

        expect(onSubmit).toHaveBeenCalledWith(edited);
        expect(await screen.findByRole('button', { name: 'Edit content' })).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Save changes' })).not.toBeInTheDocument();
    });

    it('stays in edit mode when the save fails', async () => {
        const onSubmit = vi.fn().mockRejectedValue(new Error('failed'));
        const { container } = renderWithProviders(<TextEditor initialContent={saved} onSubmit={onSubmit} />);

        await userEvent.click(await screen.findByRole('button', { name: 'Edit content' }));
        await editRichText(container, 'Edited about');
        await userEvent.click(screen.getByRole('button', { name: 'Save changes' }));

        await waitFor(() => expect(onSubmit).toHaveBeenCalled());
        expect(screen.getByRole('button', { name: 'Save changes' })).toBeInTheDocument();
    });

    it('disables editing while content is loading', async () => {
        renderWithProviders(<TextEditor initialContent={saved} onSubmit={vi.fn()} isLoading />);

        expect(await screen.findByRole('button', { name: 'Edit content' })).toBeDisabled();
    });

    it.each([undefined, null, ''])(
        'discards without confirmation when a blank page (%o) is unchanged',
        async (blank) => {
            renderWithProviders(<TextEditor initialContent={blank} onSubmit={vi.fn()} />);

            await userEvent.click(await screen.findByRole('button', { name: 'Edit content' }));
            await userEvent.click(screen.getByRole('button', { name: 'Discard changes' }));

            expect(await screen.findByRole('button', { name: 'Edit content' })).toBeInTheDocument();
            expect(screen.queryByText('Discard changes?')).not.toBeInTheDocument();
        },
    );

    it('discards unsaved edits after confirmation', async () => {
        const { container } = renderWithProviders(<TextEditor initialContent={saved} onSubmit={vi.fn()} />);

        await userEvent.click(await screen.findByRole('button', { name: 'Edit content' }));
        await editRichText(container, 'Saved about and edited');

        await userEvent.click(screen.getByRole('button', { name: 'Discard changes' }));
        await userEvent.click(await screen.findByRole('button', { name: 'Discard' }));

        expect(await screen.findByRole('button', { name: 'Edit content' })).toBeInTheDocument();
        expect(container.querySelector('[contenteditable]')).toHaveTextContent(/^Saved about$/);
    });
});
