import { describe, expect, it } from 'vitest';
import {
    DEFAULT_EXPIRING_SOON_THRESHOLD_DAYS,
    ExpiryDate,
    IsExpiringSoonTag,
    isExpiringSoon,
    RenewalTag,
} from '@/components/input-port/access-status.tsx';
import { InputPortStatus, RenewalStatus } from '@/store/api/services/generated/dataProductsApi.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

function isoInDays(days: number): string {
    const date = new Date();
    date.setDate(date.getDate() + days);
    return date.toISOString();
}

describe('isExpiringSoon', () => {
    it('is false for anything other than Approved', () => {
        expect(isExpiringSoon(InputPortStatus.Pending, isoInDays(1), DEFAULT_EXPIRING_SOON_THRESHOLD_DAYS)).toBe(false);
        expect(isExpiringSoon(InputPortStatus.Expired, isoInDays(1), DEFAULT_EXPIRING_SOON_THRESHOLD_DAYS)).toBe(false);
        expect(isExpiringSoon(InputPortStatus.Revoked, isoInDays(1), DEFAULT_EXPIRING_SOON_THRESHOLD_DAYS)).toBe(false);
    });

    it('is false when validUntil is null (permanent access)', () => {
        expect(isExpiringSoon(InputPortStatus.Approved, null, DEFAULT_EXPIRING_SOON_THRESHOLD_DAYS)).toBe(false);
    });

    it('is false when approved and well within the window', () => {
        expect(isExpiringSoon(InputPortStatus.Approved, isoInDays(30), DEFAULT_EXPIRING_SOON_THRESHOLD_DAYS)).toBe(
            false,
        );
    });

    it('is true when approved and inside the threshold', () => {
        expect(isExpiringSoon(InputPortStatus.Approved, isoInDays(5), DEFAULT_EXPIRING_SOON_THRESHOLD_DAYS)).toBe(true);
    });

    it('is false once the window has already passed', () => {
        expect(isExpiringSoon(InputPortStatus.Approved, isoInDays(-1), DEFAULT_EXPIRING_SOON_THRESHOLD_DAYS)).toBe(
            false,
        );
    });
});

describe('RenewalTag', () => {
    it('shows nothing when there is no renewal in flight', () => {
        renderWithProviders(<RenewalTag renewalStatus={null} />);
        expect(screen.queryByText('Renewal pending')).not.toBeInTheDocument();
        expect(screen.queryByText('Renewal declined')).not.toBeInTheDocument();
    });

    it('shows "Renewal pending" whenever renewalStatus is Pending, regardless of link status', () => {
        renderWithProviders(<RenewalTag renewalStatus={RenewalStatus.Pending} />);
        expect(screen.getByText('Renewal pending')).toBeInTheDocument();
    });

    it('shows "Renewal declined" when renewalStatus is Denied', () => {
        renderWithProviders(<RenewalTag renewalStatus={RenewalStatus.Denied} />);
        expect(screen.getByText('Renewal declined')).toBeInTheDocument();
    });
});

describe('ExpiryDate', () => {
    const validUntil = '2026-06-21T00:00:00Z';

    it.each([
        InputPortStatus.Pending,
        InputPortStatus.Denied,
        InputPortStatus.Revoked,
        InputPortStatus.Cancelled,
    ])('shows nothing for %s status even if validUntil is set', (status) => {
        const { container } = renderWithProviders(<ExpiryDate status={status} validUntil={validUntil} />);
        expect(container).toBeEmptyDOMElement();
    });

    it('shows "Permanent access" for Approved with no validUntil', () => {
        renderWithProviders(<ExpiryDate status={InputPortStatus.Approved} validUntil={null} />);
        expect(screen.getByText('Permanent access')).toBeInTheDocument();
    });

    it('shows the real date for Approved with a validUntil', () => {
        renderWithProviders(<ExpiryDate status={InputPortStatus.Approved} validUntil={validUntil} />);
        expect(screen.queryByText('Permanent access')).not.toBeInTheDocument();
    });

    it('shows the real date for Expired (the backend now returns the real grant`s validUntil here, not null)', () => {
        renderWithProviders(<ExpiryDate status={InputPortStatus.Expired} validUntil={validUntil} />);
        expect(screen.queryByText('Permanent access')).not.toBeInTheDocument();
    });
});

describe('IsExpiringSoonTag', () => {
    it('shows nothing when a renewal is already pending, even if expiring soon', () => {
        renderWithProviders(
            <IsExpiringSoonTag
                status={InputPortStatus.Approved}
                validUntil={isoInDays(5)}
                renewalStatus={RenewalStatus.Pending}
            />,
        );
        expect(screen.queryByText('Expiring soon')).not.toBeInTheDocument();
    });

    it('shows "Expiring soon" when approved, within the threshold and no renewal pending', async () => {
        renderWithProviders(
            <IsExpiringSoonTag status={InputPortStatus.Approved} validUntil={isoInDays(5)} renewalStatus={null} />,
        );
        expect(await screen.findByText('Expiring soon')).toBeInTheDocument();
    });
});
