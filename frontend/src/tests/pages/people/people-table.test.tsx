import { HttpResponse, http } from 'msw';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { PeoplePage } from '@/pages/people/people-table.component';
import type { GlobalRoleAssignmentResponse } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import type { Role } from '@/store/api/services/generated/authorizationRolesApi.ts';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockGroup, mockIdentitiesHttp, mockMachineUser } from '@/tests/mocks/identities.ts';
import { mockUsers, mockUsersHttp } from '@/tests/mocks/users';
import { renderWithProviders, screen, userEvent, waitFor, within } from '@/tests/test-utils.tsx';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { DecisionStatus, Prototype, Scope } from '@/types/roles';
import { getIdentityDisplayName, type Identity } from '@/utils/identity.ts';
import { server } from '../../mocks/server';

const everyone: Role = {
    id: 'everyone',
    name: 'Everyone',
    prototype: Prototype.EVERYONE,
    scope: Scope.GLOBAL,
    permissions: [],
    description: '',
};
const member: Role = { ...everyone, id: 'member', name: 'Member', prototype: Prototype.CUSTOM };
const editor: Role = { ...member, id: 'editor', name: 'Editor' };
const endpoint = '*/api/v2/authz/role_assignments/global';
const alice: Identity = { ...mockUsers[0], type: 'user' };
function globalAssignment(
    identity: Identity,
    role = member,
    decision = DecisionStatus.Approved,
): GlobalRoleAssignmentResponse {
    return {
        id: `assignment-${identity.id}`,
        identity,
        role,
        decision,
        requested_by: mockUsers[0],
        decided_by: mockUsers[0],
        requested_on: null,
        decided_on: null,
    };
}

describe('PeoplePage', () => {
    beforeEach(() => {
        allowAllAuth();
        mockIdentitiesHttp();
        server.use(
            http.get(endpoint, () => HttpResponse.json({ role_assignments: [] })),
            http.get('*/api/v2/authz/roles/global', () => HttpResponse.json({ roles: [everyone, member, editor] })),
        );
    });
    it('shows loading state while fetching', () => {
        server.use(
            http.get('*/api/v2/users', () => {
                return new Promise(() => {
                    // Never resolve call
                });
            }),
        );
        const { container } = renderWithProviders(<PeoplePage />);

        expect(container.querySelector('.ant-spin-spinning')).toBeInTheDocument();
    });

    it('renders an empty table when there are no identities', async () => {
        mockUsersHttp([]);
        server.use(
            http.get('*/api/v2/groups', () => HttpResponse.json({ groups: [] })),
            http.get('*/api/v2/machine-users', () => HttpResponse.json({ machine_users: [] })),
        );
        renderWithProviders(<PeoplePage />);

        await waitFor(() => {
            expect(screen.getByText('People')).toBeInTheDocument();
        });

        expect(
            await within(screen.getByTestId('people-table')).findByText('No identities available'),
        ).toBeInTheDocument();
    });

    it('displays users returned by the API', async () => {
        mockUsersHttp([mockUsers[0], mockUsers[1]]);
        renderWithProviders(<PeoplePage />);
        const user1 = 'alice@example.com';
        const user2 = 'bob@example.com';

        await waitFor(() => {
            expect(screen.getByText(user1)).toBeInTheDocument();
        });
        expect(screen.getByText(user1)).toBeInTheDocument();
        expect(screen.getByText(user2)).toBeInTheDocument();
    });

    it('shows an existing Admin assignment without offering Admin as an assignable role', async () => {
        const admin: Role = { ...member, id: 'admin-role', name: 'Admin', prototype: Prototype.ADMIN };
        server.use(
            http.get(endpoint, () => HttpResponse.json({ role_assignments: [globalAssignment(alice, admin)] })),
            http.get('*/api/v2/authz/roles/global', () =>
                HttpResponse.json({ roles: [everyone, member, editor, admin] }),
            ),
        );
        const user = userEvent.setup();
        renderWithProviders(<PeoplePage />);
        const row = (await screen.findByText('Alice Smith')).closest('tr');
        if (!row) throw new Error('Missing identity row');
        expect(await within(row).findByText('Admin')).toBeInTheDocument();
        expect(within(row).queryByText('Everyone')).not.toBeInTheDocument();
        const select = row.querySelector('input');
        if (!select) throw new Error('Missing global role selector');
        await waitFor(() => expect(select).toBeEnabled());
        await user.click(select);
        expect(await screen.findByText('Member', { selector: '.ant-select-item-option-content' })).toBeVisible();
        expect(screen.queryByText('Admin', { selector: '.ant-select-item-option-content' })).not.toBeInTheDocument();
    });

    it('filters users by search term', async () => {
        const user = userEvent.setup();
        mockUsersHttp([mockUsers[0], mockUsers[1]]);
        renderWithProviders(<PeoplePage />);
        const user1 = 'alice@example.com';

        await waitFor(() => {
            expect(screen.getByText(user1)).toBeInTheDocument();
        });

        const searchInput = screen.getByPlaceholderText('Search by name or identifier');
        await user.type(searchInput, 'bob');

        await waitFor(() => {
            expect(screen.queryByText(user1)).not.toBeInTheDocument();
        });
        expect(screen.getByText('bob@example.com')).toBeInTheDocument();
    });

    it('preserves the current page when searching and lets the table clamp it to the last available page', async () => {
        mockUsersHttp(
            Array.from({ length: 24 }, (_, index) => ({
                ...mockUsers[0],
                id: `user-${index}`,
                first_name: `Person ${String(index).padStart(2, '0')}`,
                email: `${index < 12 ? 'match' : 'other'}${index}@example.com`,
            })),
        );
        const user = userEvent.setup();
        renderWithProviders(<PeoplePage />);
        await screen.findByText('Showing 1-10 of 26 identities');
        await user.click(within(screen.getByTitle('3')).getByText('3'));
        expect(screen.getByText('Showing 21-26 of 26 identities')).toBeInTheDocument();

        const search = screen.getByLabelText('Search identities');
        await user.type(search, 'Person');
        expect(screen.getByText('Showing 21-24 of 24 identities')).toBeInTheDocument();
        await user.clear(search);
        expect(screen.getByText('Showing 21-26 of 26 identities')).toBeInTheDocument();
        await user.type(search, 'match');
        expect(screen.getByText('Showing 11-12 of 12 identities')).toBeInTheDocument();
        await user.clear(search);
        expect(screen.getByText('Showing 21-26 of 26 identities')).toBeInTheDocument();
    });

    it('combines email and external IDs without Name or Email column filters', async () => {
        const { container } = renderWithProviders(<PeoplePage />);
        await screen.findByText('Finance Team');
        expect(Array.from(container.querySelectorAll('thead th')).map((header) => header.textContent)).toEqual([
            'Name',
            'Identifier',
            'Type',
            'Global Role',
            'Can become admin',
        ]);
        for (const identity of [alice, mockGroup, mockMachineUser]) {
            const row = screen.getByText(getIdentityDisplayName(identity)).closest('tr');
            expect(row?.querySelectorAll('td')[1]).toHaveTextContent(
                identity.type === 'user' ? identity.email : identity.external_id,
            );
        }
        for (const name of ['Name', 'Identifier']) {
            expect(screen.getByText(name).closest('th')?.querySelector('.ant-table-filter-trigger')).toBeNull();
        }
        expect(screen.getByText('Type').closest('th')?.querySelector('.ant-table-filter-trigger')).not.toBeNull();
    });

    it.each([alice, mockGroup, mockMachineUser])(
        'assigns, changes and resets a $type global role inline',
        async (identity) => {
            let assignments: GlobalRoleAssignmentResponse[] = [];
            const create = vi.fn();
            const modify = vi.fn();
            const remove = vi.fn();
            server.use(
                http.get(endpoint, () => HttpResponse.json({ role_assignments: assignments })),
                http.post(endpoint, async ({ request }) => {
                    create(await request.json());
                    assignments = [globalAssignment(identity, member, DecisionStatus.Pending)];
                    return HttpResponse.json(assignments[0]);
                }),
                http.post(`${endpoint}/:id/decide`, () => {
                    assignments = [globalAssignment(identity)];
                    return HttpResponse.json(assignments[0]);
                }),
                http.put(`${endpoint}/:id/role`, async ({ request }) => {
                    modify(await request.json());
                    assignments = [globalAssignment(identity, editor)];
                    return HttpResponse.json(assignments[0]);
                }),
                http.delete(`${endpoint}/:id`, ({ params }) => {
                    remove(params.id);
                    assignments = [];
                    return HttpResponse.json({ id: params.id });
                }),
            );
            const user = userEvent.setup();
            renderWithProviders(<PeoplePage />);
            const row = (await screen.findByText(getIdentityDisplayName(identity))).closest('tr');
            if (!row) throw new Error('Missing identity row');
            const select = row.querySelector('input');
            if (!select) throw new Error('Missing global role selector');
            await waitFor(() => expect(select).toBeEnabled());
            await user.click(select);
            await user.click(await screen.findByText('Member', { selector: '.ant-select-item-option-content' }));
            await waitFor(() => expect(within(row).getByText('Member')).toBeInTheDocument());
            expect(create).toHaveBeenCalledExactlyOnceWith({ identity_id: identity.id, role_id: member.id });
            await waitFor(() => expect(select).toBeEnabled());
            await user.click(select);
            await user.click(await screen.findByText('Editor', { selector: '.ant-select-item-option-content' }));
            await waitFor(() => expect(within(row).getByText('Editor')).toBeInTheDocument());
            expect(modify).toHaveBeenCalledExactlyOnceWith({ role_id: editor.id });
            await waitFor(() => expect(select).toBeEnabled());
            await user.click(select);
            await user.click(await screen.findByText('Everyone', { selector: '.ant-select-item-option-content' }));
            await waitFor(() => expect(within(row).getByText('Everyone')).toBeInTheDocument());
            expect(remove).toHaveBeenCalledExactlyOnceWith(`assignment-${identity.id}`);
            expect(row.querySelector('input[type="checkbox"]') !== null).toBe(identity.type === 'user');
        },
    );

    it('keeps Name sorting active with Type and Identifier sorting while Global Role stays unsortable', async () => {
        server.use(
            http.get(endpoint, () => HttpResponse.json({ role_assignments: [globalAssignment(alice, editor)] })),
        );
        const user = userEvent.setup();
        renderWithProviders(<PeoplePage />);
        await screen.findByText('Finance Team');
        const names = () =>
            screen.getAllByText(/^(Alice Smith|Bob Jones|ETL Runner|Finance Team)$/).map((node) => node.textContent);
        const header = (name: string) => screen.getByText(name, { selector: 'th .ant-table-column-title' });
        await user.click(header('Type'));
        expect(names()).toEqual(['Finance Team', 'ETL Runner', 'Alice Smith', 'Bob Jones']);
        const roleHeader = screen.getByText('Global Role', { selector: 'th' });
        await user.click(roleHeader);
        expect(roleHeader).not.toHaveAttribute('aria-sort');
        expect(names()).toEqual(['Finance Team', 'ETL Runner', 'Alice Smith', 'Bob Jones']);
        await user.click(header('Name'));
        expect(header('Name').closest('th')).toHaveAttribute('aria-sort', 'descending');
        expect(header('Type').closest('th')).toHaveAttribute('aria-sort', 'ascending');
        expect(names()).toEqual(['Finance Team', 'ETL Runner', 'Bob Jones', 'Alice Smith']);
        await user.click(header('Identifier'));
        for (const name of ['Type', 'Identifier']) {
            await user.click(header(name));
            await user.click(header(name));
            expect(header(name).closest('th')).not.toHaveAttribute('aria-sort');
        }
        expect(names()).toEqual(['Finance Team', 'ETL Runner', 'Bob Jones', 'Alice Smith']);
        await user.click(header('Name'));
        expect(header('Name').closest('th')).toHaveAttribute('aria-sort', 'ascending');
    });

    it.each([null, DecisionStatus.Pending, DecisionStatus.Denied])(
        'retries approval without duplicating an assignment (existing: %s)',
        async (existing) => {
            let assignments: GlobalRoleAssignmentResponse[] = existing
                ? [globalAssignment(mockGroup, member, existing)]
                : [];
            const create = vi.fn();
            let attempts = 0;
            server.use(
                http.get(endpoint, () => HttpResponse.json({ role_assignments: assignments })),
                http.delete(`${endpoint}/:id`, ({ params }) => {
                    assignments = [];
                    return HttpResponse.json({ id: params.id });
                }),
                http.post(endpoint, () => {
                    create();
                    assignments = [globalAssignment(mockGroup, member, DecisionStatus.Pending)];
                    return HttpResponse.json(assignments[0]);
                }),
                http.post(`${endpoint}/:id/decide`, () => {
                    attempts++;
                    if (attempts === 1) return HttpResponse.json({ detail: 'Unavailable' }, { status: 500 });
                    assignments = [globalAssignment(mockGroup)];
                    return HttpResponse.json(assignments[0]);
                }),
            );
            const user = userEvent.setup();
            renderWithProviders(<PeoplePage />);
            const row = (await screen.findByText('Finance Team')).closest('tr');
            const select = row?.querySelector('input');
            if (!row || !select) throw new Error('Missing group role selector');
            await waitFor(() => expect(select).toBeEnabled());
            await user.click(select);
            await user.click(await screen.findByText('Member', { selector: '.ant-select-item-option-content' }));
            expect(
                await screen.findByText('Could not confirm the role assignment. Select the role again to retry.'),
            ).toBeInTheDocument();
            await waitFor(() => expect(select).toBeEnabled());
            await user.click(select);
            await user.click(await screen.findByText('Member', { selector: '.ant-select-item-option-content' }));
            await waitFor(() => expect(attempts).toBe(2));
            await waitFor(() => expect(assignments[0].decision).toBe(DecisionStatus.Approved));
            expect(within(row).getByText('Member')).toBeInTheDocument();
            expect(create).toHaveBeenCalledTimes(existing === DecisionStatus.Pending ? 0 : 1);
        },
    );

    it.each([member, editor])('recreates a denied assignment before approving $name', async (role) => {
        const denied = globalAssignment(mockGroup, member, DecisionStatus.Denied);
        let assignments = [denied];
        const requests: string[] = [];
        server.use(
            http.get(endpoint, () => HttpResponse.json({ role_assignments: assignments })),
            http.delete(`${endpoint}/:id`, ({ params }) => {
                requests.push(`delete:${params.id}`);
                assignments = [];
                return HttpResponse.json({ id: params.id });
            }),
            http.post(endpoint, async ({ request }) => {
                requests.push('create');
                expect(await request.json()).toEqual({ identity_id: mockGroup.id, role_id: role.id });
                assignments = [
                    {
                        ...globalAssignment(mockGroup, role, DecisionStatus.Pending),
                        id: 'replacement',
                    },
                ];
                return HttpResponse.json(assignments[0]);
            }),
            http.post(`${endpoint}/:id/decide`, async ({ params, request }) => {
                requests.push(`approve:${params.id}`);
                expect(await request.json()).toEqual({ decision: DecisionStatus.Approved });
                assignments[0].decision = DecisionStatus.Approved;
                return HttpResponse.json(assignments[0]);
            }),
        );
        const user = userEvent.setup();
        renderWithProviders(<PeoplePage />);
        const row = (await screen.findByText('Finance Team')).closest('tr');
        const select = row?.querySelector('input');
        if (!row || !select) throw new Error('Missing group role selector');
        await waitFor(() => expect(select).toBeEnabled());
        await user.click(select);
        await user.click(await screen.findByText(role.name, { selector: '.ant-select-item-option-content' }));
        expect(await screen.findByText('Global role successfully assigned')).toBeInTheDocument();
        expect(requests).toEqual([`delete:${denied.id}`, 'create', 'approve:replacement']);
        await waitFor(() => expect(within(row).getByText(role.name)).toBeInTheDocument());
        expect(assignments[0].decision).toBe(DecisionStatus.Approved);
    });

    it.each([alice, mockGroup, mockMachineUser])(
        'disables a denied $type role with an explanation when deletion is not allowed',
        async (identity) => {
            const denied = globalAssignment(identity, member, DecisionStatus.Denied);
            const mutate = vi.fn();
            server.use(
                http.get('*/api/v2/authz/access/:action', ({ params }) =>
                    HttpResponse.json({ allowed: Number(params.action) !== AuthorizationAction.GLOBAL__DELETE_USER }),
                ),
                http.get(endpoint, () => HttpResponse.json({ role_assignments: [denied] })),
                http.all(`${endpoint}/*`, () => {
                    mutate();
                    return HttpResponse.json({ detail: 'Forbidden' }, { status: 403 });
                }),
                http.post(endpoint, () => {
                    mutate();
                    return HttpResponse.json({ detail: 'Forbidden' }, { status: 403 });
                }),
            );
            const user = userEvent.setup();
            renderWithProviders(<PeoplePage />);
            const row = (await screen.findByText(getIdentityDisplayName(identity))).closest('tr');
            const select = row?.querySelector('input');
            if (!row || !select) throw new Error('Missing identity role selector');
            await within(row).findByText('Member');
            expect(select).toBeDisabled();
            await user.hover(within(row).getByText('Member'));
            expect(
                await screen.findByText(
                    'This role was previously rejected. You don’t have enough permission to modify it.',
                ),
            ).toBeInTheDocument();
            await user.click(within(row).getByText('Member'));
            expect(screen.queryByText('Editor', { selector: '.ant-select-item-option-content' })).toBeNull();
            expect(mutate).not.toHaveBeenCalled();
            const otherIdentity = identity.type === 'group' ? mockMachineUser : mockGroup;
            const otherSelect = screen
                .getByText(getIdentityDisplayName(otherIdentity))
                .closest('tr')
                ?.querySelector('input');
            await waitFor(() => expect(otherSelect).toBeEnabled());
        },
    );

    it.each([
        {
            status: 403,
            detail: "You don't have permission to perform this action",
        },
        { status: 500, detail: 'Unavailable' },
    ])('explains deletion failure ($status) without recreating a denied assignment', async ({ status, detail }) => {
        const denied = globalAssignment(mockGroup, member, DecisionStatus.Denied);
        const create = vi.fn();
        server.use(
            http.get(endpoint, () => HttpResponse.json({ role_assignments: [denied] })),
            http.delete(`${endpoint}/:id`, () => HttpResponse.json({ detail }, { status })),
            http.post(endpoint, () => {
                create();
                return HttpResponse.json(globalAssignment(mockGroup, editor, DecisionStatus.Pending));
            }),
        );
        const user = userEvent.setup();
        renderWithProviders(<PeoplePage />);
        const row = (await screen.findByText('Finance Team')).closest('tr');
        const select = row?.querySelector('input');
        if (!row || !select) throw new Error('Missing group role selector');
        await waitFor(() => expect(select).toBeEnabled());
        await user.click(select);
        await user.click(await screen.findByText('Editor', { selector: '.ant-select-item-option-content' }));
        expect(await screen.findByText('Could not assign global role')).toBeInTheDocument();
        await waitFor(() => expect(select).toBeEnabled());
        expect(within(row).getByText('Member')).toBeInTheDocument();
        expect(create).not.toHaveBeenCalled();
    });

    it('keeps existing roles read-only without permission and hides admin eligibility', async () => {
        server.use(
            http.get('*/api/v2/authz/access/:action', () => HttpResponse.json({ allowed: false })),
            http.get(endpoint, () => HttpResponse.json({ role_assignments: [globalAssignment(mockMachineUser)] })),
        );
        renderWithProviders(<PeoplePage />);
        expect(await screen.findByText('Member')).toBeInTheDocument();
        expect(screen.queryByText('Can become admin')).not.toBeInTheDocument();
        expect(screen.getByText('ETL Runner').closest('tr')?.querySelector('input')).toBeNull();
    });

    it('shows a retryable error instead of treating failed assignments as Everyone', async () => {
        server.use(http.get(endpoint, () => HttpResponse.json({ detail: 'Unavailable' }, { status: 500 })));
        const user = userEvent.setup();
        renderWithProviders(<PeoplePage />);
        expect(await screen.findByText("Couldn't load role assignments")).toBeInTheDocument();
        expect(screen.queryByText('Everyone')).not.toBeInTheDocument();
        server.use(http.get(endpoint, () => HttpResponse.json({ role_assignments: [globalAssignment(mockGroup)] })));
        await user.click(screen.getByText('Try again'));
        expect(await screen.findByText('Member')).toBeInTheDocument();
    });
});
