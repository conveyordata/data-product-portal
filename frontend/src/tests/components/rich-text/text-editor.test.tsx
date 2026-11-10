import { describe, expect, it, vi } from 'vitest';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor.tsx';
import { editRichText } from '@/tests/components/rich-text/text-editor.helpers.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

const saved = '<p>Saved about</p>';
const edited = '<p>Edited about</p>';

describe('TextEditor', () => {
    it('only allows saving once the content changed', async () => {
        const user = userEvent.setup();
        renderWithProviders(<TextEditor initialContent={saved} onSubmit={vi.fn()} />);

        await user.click(await screen.findByRole('button', { name: 'Edit content' }));

        expect(screen.getByRole('button', { name: 'Save changes' })).toBeDisabled();
    });

    it('saves the edited content and leaves edit mode once the save succeeds', async () => {
        const user = userEvent.setup();
        const onSubmit = vi.fn().mockResolvedValue(undefined);
        const { container } = renderWithProviders(<TextEditor initialContent={saved} onSubmit={onSubmit} />);

        await user.click(await screen.findByRole('button', { name: 'Edit content' }));
        await editRichText(container, 'Edited about');
        await user.click(screen.getByRole('button', { name: 'Save changes' }));

        expect(onSubmit).toHaveBeenCalledWith(edited);
        expect(await screen.findByRole('button', { name: 'Edit content' })).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Save changes' })).not.toBeInTheDocument();
    });

    it('stays in edit mode when the save fails', async () => {
        const user = userEvent.setup();
        const onSubmit = vi.fn().mockRejectedValue(new Error('failed'));
        const { container } = renderWithProviders(<TextEditor initialContent={saved} onSubmit={onSubmit} />);

        await user.click(await screen.findByRole('button', { name: 'Edit content' }));
        await editRichText(container, 'Edited about');
        await user.click(screen.getByRole('button', { name: 'Save changes' }));

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
            const user = userEvent.setup();
            renderWithProviders(<TextEditor initialContent={blank} onSubmit={vi.fn()} />);

            await user.click(await screen.findByRole('button', { name: 'Edit content' }));
            await user.click(screen.getByRole('button', { name: 'Discard changes' }));

            expect(await screen.findByRole('button', { name: 'Edit content' })).toBeInTheDocument();
            expect(screen.queryByText('Discard changes?')).not.toBeInTheDocument();
        },
    );

    it('discards unsaved edits after confirmation', async () => {
        const user = userEvent.setup();
        const { container } = renderWithProviders(<TextEditor initialContent={saved} onSubmit={vi.fn()} />);

        await user.click(await screen.findByRole('button', { name: 'Edit content' }));
        await editRichText(container, 'Saved about and edited');

        await user.click(screen.getByRole('button', { name: 'Discard changes' }));
        await user.click(await screen.findByRole('button', { name: 'Discard' }));

        expect(await screen.findByRole('button', { name: 'Edit content' })).toBeInTheDocument();
        expect(container.querySelector('[contenteditable]')).toHaveTextContent(/^Saved about$/);
    });
});
