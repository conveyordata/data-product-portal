import { describe, expect, it, vi } from 'vitest';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor.tsx';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

const INITIAL = '<p>Original text</p>';

function editButton() {
    return screen.getByRole('button', { name: 'Edit content' });
}

function saveButton() {
    return screen.getByRole('button', { name: 'Save changes' });
}

describe('TextEditor', () => {
    it('leaves edit mode once the save succeeds', async () => {
        const onSubmit = vi.fn().mockResolvedValue(undefined);
        renderWithProviders(<TextEditor initialContent={INITIAL} onSubmit={onSubmit} />);

        await userEvent.click(editButton());
        expect(saveButton()).toBeInTheDocument();

        await userEvent.click(saveButton());

        await waitFor(() => {
            expect(onSubmit).toHaveBeenCalledTimes(1);
        });
        await waitFor(() => {
            expect(editButton()).toBeInTheDocument();
        });
        expect(screen.queryByRole('button', { name: 'Save changes' })).not.toBeInTheDocument();
    });

    it('stays in edit mode when the save fails, so the text is not lost', async () => {
        const onSubmit = vi.fn().mockRejectedValue(new Error('save failed'));
        renderWithProviders(<TextEditor initialContent={INITIAL} onSubmit={onSubmit} />);

        await userEvent.click(editButton());
        await userEvent.click(saveButton());

        await waitFor(() => {
            expect(onSubmit).toHaveBeenCalledTimes(1);
        });
        expect(saveButton()).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Edit content' })).not.toBeInTheDocument();
    });

    it('discards without confirmation when nothing was changed', async () => {
        const onSubmit = vi.fn();
        renderWithProviders(<TextEditor initialContent={INITIAL} onSubmit={onSubmit} />);

        await userEvent.click(editButton());
        await userEvent.click(screen.getByRole('button', { name: 'Discard changes' }));

        await waitFor(() => {
            expect(editButton()).toBeInTheDocument();
        });
        expect(onSubmit).not.toHaveBeenCalled();
    });

    it('offers no editing controls when the editor is disabled', () => {
        renderWithProviders(<TextEditor initialContent={INITIAL} isDisabled />);

        expect(screen.queryByRole('button', { name: 'Edit content' })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Save changes' })).not.toBeInTheDocument();
    });
});
