import type { Editor } from '@tiptap/react';
import { describe, expect, it } from 'vitest';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor.tsx';
import { act, renderWithProviders, screen, userEvent } from '@/tests/test-utils.tsx';

async function renderEditor(user: ReturnType<typeof userEvent.setup>, initialContent: string) {
    const { container } = renderWithProviders(<TextEditor initialContent={initialContent} />);
    await user.click(await screen.findByRole('button', { name: 'Edit content' }));
    return (container.querySelector('.ProseMirror') as HTMLElement & { editor: Editor }).editor;
}

describe('TextEditorMenu', () => {
    it('bolds the selected text', async () => {
        const user = userEvent.setup();
        const editor = await renderEditor(user, '<p>plain</p>');
        act(() => {
            editor.commands.selectAll();
        });

        await user.click(screen.getByRole('button', { name: 'Bold' }));

        expect(editor.getHTML()).toBe('<p><strong>plain</strong></p>');
    });

    it('highlights Bold when the cursor moves into bold text', async () => {
        const user = userEvent.setup();
        const editor = await renderEditor(user, '<p>plain <strong>bold</strong></p>');
        act(() => {
            editor.commands.setTextSelection(2);
        });
        expect(screen.getByRole('button', { name: 'Bold' })).not.toHaveClass('ant-btn-variant-solid');

        act(() => {
            editor.commands.setTextSelection(9);
        });

        expect(screen.getByRole('button', { name: 'Bold' })).toHaveClass('ant-btn-variant-solid');
    });

    it('turns a paragraph into a heading', async () => {
        const user = userEvent.setup();
        const editor = await renderEditor(user, '<p>title</p>');

        await user.click(screen.getByRole('combobox'));
        await user.click(await screen.findByText('Heading 2'));

        expect(editor.getHTML()).toContain('<h2>title</h2>');
    });

    it('shows Text for a heading level it does not offer', async () => {
        const user = userEvent.setup();
        const editor = await renderEditor(user, '<h4>deep</h4>');
        act(() => {
            editor.commands.setTextSelection(2);
        });

        expect(screen.getByText('Text')).toBeInTheDocument();
        expect(screen.queryByText('4')).not.toBeInTheDocument();
    });
});
