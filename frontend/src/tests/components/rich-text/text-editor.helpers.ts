import { expect } from 'vitest';
import { screen, waitFor } from '@/tests/test-utils.tsx';

export async function editRichText(container: HTMLElement, text: string) {
    const paragraph = container.querySelector('[contenteditable="true"] p');
    if (!paragraph?.firstChild) throw new Error('editor is not editable');
    paragraph.firstChild.textContent = text;
    await waitFor(() => expect(screen.getByRole('button', { name: 'Save changes' })).toBeEnabled());
}
