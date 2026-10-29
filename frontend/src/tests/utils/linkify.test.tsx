import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { linkify } from '@/utils/linkify.tsx';

describe('linkify', () => {
    it('turns http(s) URLs into links without trailing punctuation', () => {
        render(<p>{linkify('See https://example.com/guide. Or http://a.io/x?y=1, javascript:alert(1)')}</p>);

        const links = screen.getAllByRole('link');
        expect(links.map((link) => link.getAttribute('href'))).toEqual([
            'https://example.com/guide',
            'http://a.io/x?y=1',
        ]);
        expect(screen.getByText(/javascript:alert\(1\)/)).toBeInTheDocument();
    });

    it('keeps text without URLs as is', () => {
        expect(linkify('No links here')).toEqual(['No links here']);
    });
});
