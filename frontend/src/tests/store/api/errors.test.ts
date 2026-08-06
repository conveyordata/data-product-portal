import { describe, expect, it } from 'vitest';
import {
    getApiErrorDetail,
    INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL,
    isIncompatibleAccessModesError,
} from '@/store/common/errors.ts';

describe('getApiErrorDetail', () => {
    it('returns undefined for non-object errors', () => {
        expect(getApiErrorDetail(undefined)).toBeUndefined();
        expect(getApiErrorDetail(null)).toBeUndefined();
        expect(getApiErrorDetail('error')).toBeUndefined();
    });

    it('returns detail from top-level detail field', () => {
        expect(getApiErrorDetail({ detail: 'Top level detail' })).toBe('Top level detail');
    });

    it('returns detail from nested data.detail field', () => {
        expect(getApiErrorDetail({ data: { detail: 'Nested detail' } })).toBe('Nested detail');
    });

    it('prefers nested data.detail over top-level detail', () => {
        expect(getApiErrorDetail({ detail: 'Top level', data: { detail: 'Nested detail' } })).toBe('Nested detail');
    });

    it('returns undefined when detail is not a string', () => {
        expect(getApiErrorDetail({ detail: { message: 'x' } })).toBeUndefined();
        expect(getApiErrorDetail({ data: { detail: ['x'] } })).toBeUndefined();
    });
});

describe('isIncompatibleAccessModesError', () => {
    it('returns true for the incompatible access modes detail', () => {
        expect(
            isIncompatibleAccessModesError({
                data: { detail: INCOMPATIBLE_ACCESS_MODES_ERROR_DETAIL },
            }),
        ).toBe(true);
    });

    it('returns false for other details', () => {
        expect(
            isIncompatibleAccessModesError({
                data: { detail: 'Some other error' },
            }),
        ).toBe(false);
    });
});
