import type { Editor } from '@tiptap/react';
import { act } from 'react';
import { describe, expect, it } from 'vitest';
import { TextEditor } from '@/components/rich-text/text-editor/text-editor.tsx';
import { renderWithProviders, screen, userEvent } from '../../test-utils';

function renderEditor(initialContent: string) {
    const { container } = renderWithProviders(<TextEditor initialContent={initialContent} isInitialEditMode />);
    return (container.querySelector('.ProseMirror') as HTMLElement & { editor: Editor }).editor;
}

describe('TextEditorMenu', () => {
    it('bolds the selected text', async () => {
        const editor = renderEditor('<p>plain</p>');
        act(() => {
            editor.commands.selectAll();
        });

        await userEvent.click(screen.getByRole('button', { name: 'Bold' }));

        expect(editor.getHTML()).toBe('<p><strong>plain</strong></p>');
    });

    it('highlights Bold when the cursor moves into bold text', async () => {
        const editor = renderEditor('<p>plain <strong>bold</strong></p>');
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
        const editor = renderEditor('<p>title</p>');

        await userEvent.click(screen.getByRole('combobox'));
        await userEvent.click(await screen.findByText('Heading 2'));

        expect(editor.getHTML()).toContain('<h2>title</h2>');
    });

    it('shows Text for a heading level it does not offer', () => {
        const editor = renderEditor('<h4>deep</h4>');
        act(() => {
            editor.commands.setTextSelection(2);
        });

        expect(screen.getByText('Text')).toBeInTheDocument();
        expect(screen.queryByText('4')).not.toBeInTheDocument();
    });
});
