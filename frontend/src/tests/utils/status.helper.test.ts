import { describe, expect, it } from 'vitest';
import i18n from '@/tests/i18n.ts';
import { DecisionStatus } from '@/types/roles';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper.ts';

const t = i18n.t.bind(i18n);

describe('getDecisionStatusLabel', () => {
    it('shows "Available" for an approved request that was never revoked', () => {
        expect(getDecisionStatusLabel(t, DecisionStatus.Approved)).toBe('Available');
    });

    it('shows "Revoked", not "Available", for an approved request whose access was later revoked', () => {
        expect(getDecisionStatusLabel(t, DecisionStatus.Approved, '2026-07-01T00:00:00Z')).toBe('Revoked');
    });

    it('ignores revokedAt for a request that was never approved', () => {
        expect(getDecisionStatusLabel(t, DecisionStatus.Denied, null)).toBe('Rejected');
    });
});

describe('getDecisionStatusBadgeStatus', () => {
    it('shows "success" for an approved request that was never revoked', () => {
        expect(getDecisionStatusBadgeStatus(DecisionStatus.Approved)).toBe('success');
    });

    it('shows "error" for an approved request whose access was later revoked', () => {
        expect(getDecisionStatusBadgeStatus(DecisionStatus.Approved, '2026-07-01T00:00:00Z')).toBe('error');
    });
});
