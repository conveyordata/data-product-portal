import { describe, expect, it, vi } from 'vitest';
import { InputPortActionButton } from '@/components/abstract-data-products/input-port-tab/components/input-port-table/input-port-action-button.component.tsx';
import {
    InputPortStatus,
    type OutputPort,
    OutputPortAccessType,
    OutputPortStatus,
    RenewalStatus,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

const outputPort: OutputPort = {
    id: 'output-port-1',
    name: 'Test Output Port',
    namespace: 'test',
    description: '',
    status: OutputPortStatus.Active,
    access_type: OutputPortAccessType.Restricted,
    data_product_id: 'dp-1',
    tags: [],
};

function isoInDays(days: number): string {
    const date = new Date();
    date.setDate(date.getDate() + days);
    return date.toISOString();
}

const FAR_FUTURE = isoInDays(365);
const EXPIRING_SOON = isoInDays(5);

type Buttons = {
    renew: boolean;
    cancel: boolean;
    revoke: boolean;
};

function renderButton(status: InputPortStatus, renewalStatus: RenewalStatus | null, validUntil: string | null) {
    renderWithProviders(
        <InputPortActionButton
            output_port={outputPort}
            canRemoveAccess={true}
            canRequestAccess={true}
            handleCancel={vi.fn()}
            handleRevoke={vi.fn()}
            handleRenew={vi.fn()}
            status={status}
            validUntil={validUntil}
            renewalStatus={renewalStatus}
        />,
    );
}

function visibleButtons(): Buttons {
    return {
        renew: screen.queryByText('Renew Access') !== null,
        cancel: screen.queryByText('Cancel Request') !== null,
        revoke: screen.queryByText('Revoke Access') !== null,
    };
}

describe('InputPortActionButton', () => {
    it.each<[string, InputPortStatus, RenewalStatus | null, string | null, Buttons]>([
        [
            'Approved, active, far from expiry, no renewal in flight',
            InputPortStatus.Approved,
            null,
            FAR_FUTURE,
            { renew: false, cancel: false, revoke: true },
        ],
        [
            'Approved, active, expiring soon',
            InputPortStatus.Approved,
            null,
            EXPIRING_SOON,
            { renew: true, cancel: false, revoke: true },
        ],
        [
            'Approved, active grant with a pending renewal',
            InputPortStatus.Approved,
            RenewalStatus.Pending,
            FAR_FUTURE,
            { renew: false, cancel: true, revoke: true },
        ],
        [
            'Approved, active grant with a declined renewal',
            InputPortStatus.Approved,
            RenewalStatus.Denied,
            FAR_FUTURE,
            { renew: false, cancel: false, revoke: true },
        ],
        [
            'Pending, first-ever request',
            InputPortStatus.Pending,
            null,
            null,
            { renew: false, cancel: true, revoke: false },
        ],
        [
            'Expired, no renewal requested',
            InputPortStatus.Expired,
            null,
            FAR_FUTURE,
            { renew: true, cancel: false, revoke: false },
        ],
        [
            'Expired, renewal now pending',
            InputPortStatus.Expired,
            RenewalStatus.Pending,
            FAR_FUTURE,
            { renew: false, cancel: true, revoke: false },
        ],
        ['Denied, no other request', InputPortStatus.Denied, null, null, { renew: true, cancel: false, revoke: false }],
        [
            'Revoked, no other request -> Renew only',
            InputPortStatus.Revoked,
            null,
            null,
            { renew: true, cancel: false, revoke: false },
        ],
        [
            'Revoked, then requested access again (now pending)',
            InputPortStatus.Revoked,
            RenewalStatus.Pending,
            null,
            { renew: false, cancel: true, revoke: false },
        ],
        ['Cancelled', InputPortStatus.Cancelled, null, null, { renew: true, cancel: false, revoke: false }],
    ])('%s', (_description, status, renewalStatus, validUntil, expected) => {
        renderButton(status, renewalStatus, validUntil);
        expect(visibleButtons()).toEqual(expected);
    });
});
