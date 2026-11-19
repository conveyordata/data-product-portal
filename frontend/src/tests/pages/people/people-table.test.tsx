import { HttpResponse, http } from 'msw';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { PeoplePage } from '@/pages/people/people-table.component';
import type { GlobalRoleAssignmentResponse } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import type { Role } from '@/store/api/services/generated/authorizationRolesApi.ts';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockGroup, mockIdentitiesHttp, mockMachineUser } from '@/tests/mocks/identities.ts';
import { mockUsers, mockUsersHttp } from '@/tests/mocks/users';
import { renderWithProviders, screen, userEvent, waitFor, within } from '@/tests/test-utils.tsx';
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

    it('filters users by search term', async () => {
        const user = userEvent.setup();
        mockUsersHttp([mockUsers[0], mockUsers[1]]);
        renderWithProviders(<PeoplePage />);
        const user1 = 'alice@example.com';

        await waitFor(() => {
            expect(screen.getByText(user1)).toBeInTheDocument();
        });

        const searchInput = screen.getByPlaceholderText('Search by name, email, or external ID');
        await user.type(searchInput, 'bob');

        await waitFor(() => {
            expect(screen.queryByText(user1)).not.toBeInTheDocument();
        });
        expect(screen.getByText('bob@example.com')).toBeInTheDocument();
    });

    it('combines email and external IDs without Name or Email column filters', async () => {
        const { container } = renderWithProviders(<PeoplePage />);
        await screen.findByText('Finance Team');
        expect(Array.from(container.querySelectorAll('thead th')).map((header) => header.textContent)).toEqual([
            'Name',
            'Email / External ID',
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
        for (const name of ['Name', 'Email / External ID']) {
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

    it('keeps Name sorting active while combining Type, Email and Global Role sorting', async () => {
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
        await user.click(header('Global Role'));
        await user.click(header('Name'));
        expect(header('Name').closest('th')).toHaveAttribute('aria-sort', 'descending');
        expect(header('Type').closest('th')).toHaveAttribute('aria-sort', 'ascending');
        expect(header('Global Role').closest('th')).toHaveAttribute('aria-sort', 'ascending');
        expect(names()).toEqual(['Finance Team', 'ETL Runner', 'Alice Smith', 'Bob Jones']);
        await user.click(header('Email / External ID'));
        for (const name of ['Type', 'Email / External ID', 'Global Role']) {
            await user.click(header(name));
            await user.click(header(name));
            expect(header(name).closest('th')).not.toHaveAttribute('aria-sort');
        }
        expect(names()).toEqual(['Finance Team', 'ETL Runner', 'Bob Jones', 'Alice Smith']);
        await user.click(header('Name'));
        expect(header('Name').closest('th')).toHaveAttribute('aria-sort', 'ascending');
    });

    it('retries approval of the same role without creating a duplicate assignment', async () => {
        let assignments: GlobalRoleAssignmentResponse[] = [];
        const create = vi.fn();
        let attempts = 0;
        server.use(
            http.get(endpoint, () => HttpResponse.json({ role_assignments: assignments })),
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
        expect(await screen.findByText('Could not assign global role')).toBeInTheDocument();
        await waitFor(() => expect(select).toBeEnabled());
        await user.click(select);
        await user.click(await screen.findByText('Member', { selector: '.ant-select-item-option-content' }));
        await waitFor(() => expect(attempts).toBe(2));
        await waitFor(() => expect(assignments[0].decision).toBe(DecisionStatus.Approved));
        expect(within(row).getByText('Member')).toBeInTheDocument();
        expect(create).toHaveBeenCalledTimes(1);
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
