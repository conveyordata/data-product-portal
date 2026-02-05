import { describe, expect, it } from 'vitest';
import translations from '../../public/locales/en/translation.json';

type GlossaryRule = {
    expected: string; // The expected capitalization
    pattern: RegExp; // Regex to find all case-variants (e.g., /output port/i)
};

const GLOSSARY_TERMS: GlossaryRule[] = [
    {
        expected: 'Data Product',
        pattern: /data product/i,
    },
    {
        expected: 'Output Port',
        pattern: /output port/i,
    },
    {
        expected: 'Input Port',
        pattern: /input port/i,
    },
    {
        expected: 'Technical Asset',
        pattern: /techincal asset/i,
    },
];

describe('Glossary Enforcement', () => {
    GLOSSARY_TERMS.forEach(({ expected, pattern }) => {
        it(`should enforce strict casing for "${expected}"`, () => {
            Object.entries(translations).forEach(([key, text]) => {
                const matches = [...(text.match(pattern) ?? []), ...(key.match(pattern) ?? [])];
                matches.forEach((match) => {
                    expect(match).toEqual(expected);
                });
            });
        });
    });
});
