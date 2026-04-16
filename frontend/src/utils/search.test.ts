import { describe } from 'vitest';
import { cleanupForSearching } from '@/utils/search.ts';

describe('cleanupForSearching', () => {
    it('Should remove accents', () => {
        expect(cleanupForSearching('bléê')).toEqual('blee');
    });

    it('Should keep email the same', () => {
        expect(cleanupForSearching('name@example.com')).toEqual('name@example.com');
    });

    it('Should remove casing', () => {
        expect(cleanupForSearching('BlaBla')).toEqual('blabla');
    });
});
