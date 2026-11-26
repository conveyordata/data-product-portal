import { HttpResponse, http } from 'msw';
import { describe, expect, it, vi } from 'vitest';
import { IdentitySelector } from '@/components/identity-selector/identity-selector.component.tsx';
import type { GroupsGetResponse } from '@/store/api/services/generated/groupsApi.ts';
import type { MachineUsersGetResponse } from '@/store/api/services/generated/machineUsersApi.ts';
import type { GetUsersResponse } from '@/store/api/services/generated/usersApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockUsers } from '@/tests/mocks/users.ts';
import { renderWithProviders, screen, userEvent, waitFor, within } from '@/tests/test-utils.tsx';
import { getIdentityDisplayName } from '@/utils/identity.ts';

const groups: GroupsGetResponse['groups'] = [
    { id: 'group-1', display_name: 'Finance Team', external_id: 'team-finance-external' },
];
const machineUsers: MachineUsersGetResponse['machine_users'] = [
    { id: 'machine-1', display_name: 'ETL Runner', external_id: 'service-principal-id' },
];

function mockIdentities(users = mockUsers, availableGroups = groups, availableMachineUsers = machineUsers) {
    const responses = {
        users: { users } satisfies GetUsersResponse,
        groups: { groups: availableGroups } satisfies GroupsGetResponse,
        machineUsers: { machine_users: availableMachineUsers } satisfies MachineUsersGetResponse,
    };
    const handlers = {
        users: vi.fn(() => HttpResponse.json(responses.users)),
        groups: vi.fn(() => HttpResponse.json(responses.groups)),
        machineUsers: vi.fn(() => HttpResponse.json(responses.machineUsers)),
    };
    server.use(
        http.get('*/api/v2/users', handlers.users),
        http.get('*/api/v2/groups', handlers.groups),
        http.get('*/api/v2/machine-users', handlers.machineUsers),
    );
    return handlers;
}

function filterMenu() {
    const menu = document.querySelector<HTMLElement>('.ant-table-filter-dropdown');
    if (!menu) throw new Error('Type filter is not open');
    return within(menu);
}

describe('IdentitySelector', () => {
    it('renders caller actions in a separate unsortable last column without selecting rows', async () => {
        mockIdentities();
        const user = userEvent.setup();
        const onAction = vi.fn();
        renderWithProviders(
            <IdentitySelector
                actionTitle="Add member"
                renderAction={(identity, disabled) => (
                    <button type="button" disabled={disabled} onClick={() => onAction(identity)}>
                        Use {getIdentityDisplayName(identity)}
                    </button>
                )}
            />,
        );
        await screen.findByText('Alice Smith');
        const cell = screen.getByText('Alice Smith').closest('td');
        if (!cell) throw new Error('Missing Name cell');
        expect(within(cell).queryByText('Use Alice Smith')).not.toBeInTheDocument();
        expect(screen.getByText('Use Alice Smith').closest('td')).toBe(cell.parentElement?.lastElementChild);
        expect(screen.getByText('Add member', { selector: 'th' })).not.toHaveAttribute('aria-sort');
        await user.click(screen.getByText('Alice Smith'));
        expect(onAction).not.toHaveBeenCalled();
        expect(screen.queryByText('Actions')).not.toBeInTheDocument();
        await user.click(screen.getByText('Use Alice Smith'));
        await user.click(screen.getByText('Use Finance Team'));
        await user.click(screen.getByText('Use ETL Runner'));
        expect(onAction).toHaveBeenNthCalledWith(1, expect.objectContaining({ id: '1', type: 'user' }));
        expect(onAction).toHaveBeenNthCalledWith(2, expect.objectContaining({ id: 'group-1', type: 'group' }));
        expect(onAction).toHaveBeenNthCalledWith(3, expect.objectContaining({ id: 'machine-1', type: 'machine_user' }));
    });

    it.each([
        ['  ALICE SMITH  ', 'Alice Smith'],
        ['ALICE@EXAMPLE.COM', 'Alice Smith'],
        ['FINANCE TEAM', 'Finance Team'],
        ['ETL RUNNER', 'ETL Runner'],
        ['EXT-1', 'Alice Smith'],
        ['TEAM-FINANCE-EXTERNAL', 'Finance Team'],
        ['SERVICE-PRINCIPAL-ID', 'ETL Runner'],
    ])('searches %s locally', async (search, expectedName) => {
        const handlers = mockIdentities();
        const user = userEvent.setup();
        renderWithProviders(<IdentitySelector />);
        await screen.findByText('Alice Smith');
        await user.type(screen.getByLabelText('Search identities'), search);
        expect(screen.getByText('Showing 1-1 of 1 identities')).toBeInTheDocument();
        expect(screen.getByText(expectedName)).toBeInTheDocument();
        for (const handler of Object.values(handlers)) {
            expect(handler).toHaveBeenCalledTimes(1);
        }
    });

    it('preserves the page when searching, clamps it to the last page, and resets it for header filters', async () => {
        const users = Array.from({ length: 24 }, (_, index) => ({
            ...mockUsers[0],
            id: `user-${index}`,
            first_name: `Person ${String(index).padStart(2, '0')}`,
            last_name: 'User',
            email: `${index < 12 ? 'match' : 'other'}${index}@example.com`,
            external_id: `external-${index}`,
        }));
        const handlers = mockIdentities(users);
        const user = userEvent.setup();
        renderWithProviders(<IdentitySelector />);
        await screen.findByText('Person 00 User');
        expect(screen.getByText('Showing 1-10 of 26 identities')).toBeInTheDocument();
        await user.click(within(screen.getByTitle('3')).getByText('3'));
        expect(screen.getByText('Showing 21-26 of 26 identities')).toBeInTheDocument();
        const search = screen.getByLabelText('Search identities');
        await user.type(search, 'Person');
        expect(screen.getByText('Showing 21-24 of 24 identities')).toBeInTheDocument();
        await user.clear(search);
        await user.type(search, 'match');
        expect(screen.getByText('Showing 11-12 of 12 identities')).toBeInTheDocument();
        expect(screen.getByText('Person 10 User')).toBeInTheDocument();
        await user.clear(search);
        expect(screen.getByText('Showing 21-26 of 26 identities')).toBeInTheDocument();
        await user.click(screen.getByLabelText('filter', { selector: 'th [aria-label]' }));
        await user.click(filterMenu().getByText('Group'));
        await user.click(filterMenu().getByText('Machine User'));
        await user.click(filterMenu().getByText('OK'));
        expect(screen.getByText('Showing 1-2 of 2 identities')).toBeInTheDocument();
        expect(screen.getByText('Finance Team')).toBeInTheDocument();
        expect(screen.getByText('ETL Runner')).toBeInTheDocument();
        await user.type(search, 'Alice');
        expect(screen.getByText('No identities match "Alice" with the current filters')).toBeInTheDocument();
        await user.click(screen.getByText('Clear filters'));
        expect(screen.getByText('Person 00 User')).toBeInTheDocument();
        expect(screen.getByText('Showing 1-10 of 26 identities')).toBeInTheDocument();
        for (const handler of Object.values(handlers)) {
            expect(handler).toHaveBeenCalledTimes(1);
        }
    });

    it('cycles Type through both directions and unsorted while keeping Name sorting active', async () => {
        mockIdentities();
        const user = userEvent.setup();
        renderWithProviders(<IdentitySelector />);
        await screen.findByText('Alice Smith');
        const names = () =>
            screen.getAllByText(/^(Alice Smith|Bob Jones|ETL Runner|Finance Team)$/).map((name) => name.textContent);
        const typeHeader = screen.getByText('Type', { selector: 'th .ant-table-column-title' });
        const nameHeader = screen.getByText('Name', { selector: 'th .ant-table-column-title' });
        expect(typeHeader.closest('th')).not.toHaveAttribute('aria-sort');
        expect(nameHeader.closest('th')).toHaveAttribute('aria-sort', 'ascending');
        expect(names()).toEqual(['Alice Smith', 'Bob Jones', 'ETL Runner', 'Finance Team']);
        await user.click(typeHeader);
        expect(typeHeader.closest('th')).toHaveAttribute('aria-sort', 'ascending');
        expect(names()).toEqual(['Finance Team', 'ETL Runner', 'Alice Smith', 'Bob Jones']);
        await user.click(typeHeader);
        expect(typeHeader.closest('th')).toHaveAttribute('aria-sort', 'descending');
        expect(names()).toEqual(['Alice Smith', 'Bob Jones', 'ETL Runner', 'Finance Team']);
        await user.click(nameHeader);
        expect(nameHeader.closest('th')).toHaveAttribute('aria-sort', 'descending');
        expect(typeHeader.closest('th')).toHaveAttribute('aria-sort', 'descending');
        expect(names()).toEqual(['Bob Jones', 'Alice Smith', 'ETL Runner', 'Finance Team']);
        await user.click(typeHeader);
        expect(typeHeader.closest('th')).not.toHaveAttribute('aria-sort');
        expect(nameHeader.closest('th')).toHaveAttribute('aria-sort', 'descending');
        expect(names()).toEqual(['Finance Team', 'ETL Runner', 'Bob Jones', 'Alice Smith']);
        await user.click(nameHeader);
        expect(nameHeader.closest('th')).toHaveAttribute('aria-sort', 'ascending');
        expect(names()).toEqual(['Alice Smith', 'Bob Jones', 'ETL Runner', 'Finance Team']);
        await user.click(typeHeader);
        expect(typeHeader.closest('th')).toHaveAttribute('aria-sort', 'ascending');
        expect(nameHeader.closest('th')).toHaveAttribute('aria-sort', 'ascending');
        expect(names()).toEqual(['Finance Team', 'ETL Runner', 'Alice Smith', 'Bob Jones']);
    });

    it('distinguishes an empty directory from a failed request or filtered result', async () => {
        mockIdentities([], [], []);
        renderWithProviders(<IdentitySelector />);
        expect(await screen.findByText('No identities available')).toBeInTheDocument();
        expect(screen.queryByText('Try again')).not.toBeInTheDocument();
        expect(screen.queryByText('Clear filters')).not.toBeInTheDocument();
    });

    it.each(['users', 'groups', 'machine-users'])(
        'shows a retryable error instead of a partial list when %s cannot load',
        async (endpoint) => {
            mockIdentities();
            server.use(
                http.get(`*/api/v2/${endpoint}`, () =>
                    HttpResponse.json({ detail: 'Identity service unavailable' }, { status: 500 }),
                ),
            );
            const user = userEvent.setup();
            renderWithProviders(<IdentitySelector />);
            expect(await screen.findByText("Couldn't load identities")).toBeInTheDocument();
            expect(screen.queryByText('Alice Smith')).not.toBeInTheDocument();
            expect(screen.queryByText('Finance Team')).not.toBeInTheDocument();
            expect(screen.queryByText('ETL Runner')).not.toBeInTheDocument();
            mockIdentities();
            await user.click(screen.getByText('Try again'));
            expect(await screen.findByText('Alice Smith')).toBeInTheDocument();
            expect(screen.getByText('Finance Team')).toBeInTheDocument();
            expect(screen.getByText('ETL Runner')).toBeInTheDocument();
        },
    );

    it('excludes identities already handled by the caller and disables actions while busy', async () => {
        mockIdentities();
        const renderAction = (_: unknown, disabled: boolean) => (
            <button type="button" disabled={disabled}>
                Assign
            </button>
        );
        const { rerender } = renderWithProviders(
            <IdentitySelector renderAction={renderAction} identityIdsToHide={['group-1']} disabled />,
        );
        await screen.findByText('Alice Smith');
        expect(screen.queryByText('Finance Team')).not.toBeInTheDocument();
        for (const button of screen.getAllByText('Assign')) expect(button).toBeDisabled();
        rerender(<IdentitySelector renderAction={renderAction} identityIdsToHide={['group-1']} />);
        await waitFor(() => {
            for (const button of screen.getAllByText('Assign')) expect(button).toBeEnabled();
        });
    });
});
