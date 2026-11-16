import { HttpResponse, http } from 'msw';
import { describe, expect, it, vi } from 'vitest';
import { IdentitySelector } from '@/components/identity-selector/identity-selector.component.tsx';
import type { GroupsGetResponse } from '@/store/api/services/generated/groupsApi.ts';
import type { MachineUsersGetResponse } from '@/store/api/services/generated/machineUsersApi.ts';
import type { GetUsersResponse } from '@/store/api/services/generated/usersApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockUsers } from '@/tests/mocks/users.ts';
import { renderWithProviders, screen, userEvent, waitFor, within } from '@/tests/test-utils.tsx';

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

describe('IdentitySelector', () => {
    it('shows every identity type and returns the selected identity', async () => {
        mockIdentities();
        const user = userEvent.setup();
        const onSelect = vi.fn();
        renderWithProviders(<IdentitySelector onSelect={onSelect} />);

        const userRow = await screen.findByRole('row', { name: /Alice Smith/ });
        expect(within(userRow).getByText('alice@example.com')).toBeInTheDocument();
        expect(within(userRow).getByText('User')).toBeInTheDocument();
        const groupRow = screen.getByRole('row', { name: /Finance Team/ });
        expect(within(groupRow).getByText('Group')).toBeInTheDocument();
        const machineRow = screen.getByRole('row', { name: /ETL Runner/ });
        expect(within(machineRow).getByText('Machine User')).toBeInTheDocument();

        await user.click(within(userRow).getByRole('button', { name: 'Select Alice Smith (User)' }));
        await user.click(within(groupRow).getByRole('button', { name: 'Select Finance Team (Group)' }));
        await user.click(within(machineRow).getByRole('button', { name: 'Select ETL Runner (Machine User)' }));

        expect(onSelect).toHaveBeenNthCalledWith(1, expect.objectContaining({ id: '1', type: 'user' }));
        expect(onSelect).toHaveBeenNthCalledWith(2, expect.objectContaining({ id: 'group-1', type: 'group' }));
        expect(onSelect).toHaveBeenNthCalledWith(3, expect.objectContaining({ id: 'machine-1', type: 'machine_user' }));
    });

    it.each([
        ['  ALICE SMITH  ', 'Alice Smith'],
        ['ALICE@EXAMPLE.COM', 'Alice Smith'],
        ['EXT-1', 'Alice Smith'],
        ['FINANCE TEAM', 'Finance Team'],
        ['TEAM-FINANCE-EXTERNAL', 'Finance Team'],
        ['ETL RUNNER', 'ETL Runner'],
        ['SERVICE-PRINCIPAL-ID', 'ETL Runner'],
    ])('searches %s locally', async (search, expectedName) => {
        const handlers = mockIdentities();
        const user = userEvent.setup();
        renderWithProviders(<IdentitySelector onSelect={vi.fn()} />);
        await screen.findByText('Alice Smith');

        await user.type(screen.getByRole('searchbox', { name: 'Search identities' }), search);

        expect(screen.getAllByRole('row')).toHaveLength(2);
        expect(screen.getByText(expectedName)).toBeInTheDocument();
        for (const handler of Object.values(handlers)) {
            expect(handler).toHaveBeenCalledTimes(1);
        }
    });

    it('paginates locally and returns to the first page when search or types change', async () => {
        const users = Array.from({ length: 12 }, (_, index) => ({
            ...mockUsers[0],
            id: `user-${index}`,
            first_name: `Person ${String(index).padStart(2, '0')}`,
            last_name: 'User',
            email: `person${index}@example.com`,
            external_id: `external-${index}`,
        }));
        const handlers = mockIdentities(users);
        const user = userEvent.setup();
        renderWithProviders(<IdentitySelector onSelect={vi.fn()} />);
        await screen.findByText('Person 00 User');

        expect(screen.getAllByRole('row')).toHaveLength(11);
        expect(screen.getByText('Showing 1-10 of 14 identities')).toBeInTheDocument();
        await user.click(within(screen.getByTitle('2')).getByRole('button'));
        await waitFor(() => expect(screen.getAllByRole('row')).toHaveLength(5));
        expect(screen.getByText('Showing 11-14 of 14 identities')).toBeInTheDocument();

        const search = screen.getByRole('searchbox', { name: 'Search identities' });
        await user.type(search, 'person0@example.com');
        expect(screen.getByText('Person 00 User')).toBeInTheDocument();
        expect(screen.getByText('Showing 1-1 of 1 identities')).toBeInTheDocument();

        await user.clear(search);
        await user.click(within(screen.getByTitle('2')).getByRole('button'));
        await user.click(screen.getByRole('checkbox', { name: 'Users' }));
        expect(screen.getByText('Showing 1-2 of 2 identities')).toBeInTheDocument();
        expect(screen.getByText('Finance Team')).toBeInTheDocument();
        expect(screen.getByText('ETL Runner')).toBeInTheDocument();
        for (const handler of Object.values(handlers)) {
            expect(handler).toHaveBeenCalledTimes(1);
        }
    });

    it('starts with all types selected and can exclude every type or clear the filters', async () => {
        mockIdentities();
        const user = userEvent.setup();
        renderWithProviders(<IdentitySelector onSelect={vi.fn()} />);
        await screen.findByText('Alice Smith');

        for (const label of ['Users', 'Groups', 'Machine Users']) {
            const checkbox = screen.getByRole('checkbox', { name: label });
            expect(checkbox).toBeChecked();
            await user.click(checkbox);
        }
        expect(screen.getByText('No identities match the current filters')).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: /^Select / })).not.toBeInTheDocument();

        await user.click(screen.getByRole('button', { name: 'Clear filters' }));
        expect(screen.getByText('Alice Smith')).toBeInTheDocument();
        expect(screen.getByText('Finance Team')).toBeInTheDocument();
        expect(screen.getByText('ETL Runner')).toBeInTheDocument();
        for (const checkbox of screen.getAllByRole('checkbox')) {
            expect(checkbox).toBeChecked();
        }
    });

    it('distinguishes an empty directory from a failed request or filtered result', async () => {
        mockIdentities([], [], []);
        renderWithProviders(<IdentitySelector onSelect={vi.fn()} />);

        expect(await screen.findByText('No identities available')).toBeInTheDocument();
        expect(
            screen.getByText('There are no users, groups, or machine users available to select.'),
        ).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Try again' })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Clear filters' })).not.toBeInTheDocument();
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
            renderWithProviders(<IdentitySelector onSelect={vi.fn()} />);

            expect(await screen.findByText("Couldn't load identities")).toBeInTheDocument();
            expect(screen.queryByText('Alice Smith')).not.toBeInTheDocument();
            expect(screen.queryByText('Finance Team')).not.toBeInTheDocument();
            expect(screen.queryByText('ETL Runner')).not.toBeInTheDocument();

            mockIdentities();
            await user.click(screen.getByRole('button', { name: 'Try again' }));
            expect(await screen.findByText('Alice Smith')).toBeInTheDocument();
            expect(screen.getByText('Finance Team')).toBeInTheDocument();
            expect(screen.getByText('ETL Runner')).toBeInTheDocument();
        },
    );

    it('excludes identities already handled by the caller and disables selection while busy', async () => {
        mockIdentities();
        const user = userEvent.setup();
        const onSelect = vi.fn();
        const { rerender } = renderWithProviders(
            <IdentitySelector onSelect={onSelect} identityIdsToHide={['group-1']} disabled />,
        );
        await screen.findByText('Alice Smith');
        expect(screen.queryByText('Finance Team')).not.toBeInTheDocument();
        const selectUser = screen.getByRole('button', { name: 'Select Alice Smith (User)' });
        expect(selectUser).toBeDisabled();
        await user.click(selectUser);
        expect(onSelect).not.toHaveBeenCalled();

        rerender(<IdentitySelector onSelect={onSelect} identityIdsToHide={['group-1']} />);
        await waitFor(() => expect(selectUser).toBeEnabled());
        await user.click(selectUser);
        expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ id: '1', type: 'user' }));
    });
});
