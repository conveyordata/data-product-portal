import { describe, expect, it, vi } from 'vitest';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor.tsx';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

const saved = '<p>Saved about</p>';

describe('TextEditor', () => {
    it('leaves edit mode once the save succeeds', async () => {
        const onSubmit = vi.fn().mockResolvedValue(undefined);
        renderWithProviders(<TextEditor initialContent={saved} onSubmit={onSubmit} />);

        await userEvent.click(await screen.findByRole('button', { name: 'Edit content' }));
        await userEvent.click(screen.getByRole('button', { name: 'Save changes' }));

        expect(onSubmit).toHaveBeenCalledWith(saved);
        expect(await screen.findByRole('button', { name: 'Edit content' })).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Save changes' })).not.toBeInTheDocument();
    });

    it('stays in edit mode when the save fails', async () => {
        const onSubmit = vi.fn().mockRejectedValue(new Error('failed'));
        renderWithProviders(<TextEditor initialContent={saved} onSubmit={onSubmit} />);

        await userEvent.click(await screen.findByRole('button', { name: 'Edit content' }));
        await userEvent.click(screen.getByRole('button', { name: 'Save changes' }));

        await waitFor(() => expect(onSubmit).toHaveBeenCalled());
        expect(screen.getByRole('button', { name: 'Save changes' })).toBeInTheDocument();
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
        const paragraph = container.querySelector('[contenteditable="true"] p');
        if (!paragraph?.firstChild) throw new Error('editor is not editable');
        paragraph.firstChild.textContent = 'Saved about and edited';

        await userEvent.click(screen.getByRole('button', { name: 'Discard changes' }));
        await userEvent.click(await screen.findByRole('button', { name: 'Discard' }));

        expect(await screen.findByRole('button', { name: 'Edit content' })).toBeInTheDocument();
        expect(container.querySelector('[contenteditable]')).toHaveTextContent(/^Saved about$/);
    });
});
