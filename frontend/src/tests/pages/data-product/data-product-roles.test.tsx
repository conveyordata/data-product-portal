import { HttpResponse, http } from 'msw';
import { describe, expect, it, vi } from 'vitest';
import { IdentityAccessOverview } from '@/components/data-access/identity-access-overview/identity-access-overview.component.tsx';
import { DataProductRequestAccessButton } from '@/pages/data-product/components/data-product-request-access-button/data-product-request-access-button.tsx';
import { TeamTab } from '@/pages/data-product/components/data-product-tabs/team-tab/team-tab.tsx';
import { PendingAccessRequestsTab } from '@/pages/product-studio/components/pending-access-requests-tab/pending-access-requests-tab.tsx';
import type { DataProductRoleAssignmentResponse } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import type { Role } from '@/store/api/services/generated/authorizationRolesApi.ts';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockDataProducts } from '@/tests/mocks/dataProducts.ts';
import { mockGroup, mockIdentitiesHttp, mockMachineUser } from '@/tests/mocks/identities.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockUsers } from '@/tests/mocks/users.ts';
import { renderWithProviders, screen, userEvent, waitFor, within } from '@/tests/test-utils.tsx';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { RequestType_DataProductRoleAssignment } from '@/types/request-types/request-types.tsx';
import { DecisionStatus, Prototype, Scope } from '@/types/roles';
import type { Identity } from '@/utils/identity.ts';

const endpoint = '*/api/v2/authz/role_assignments/data_product';
const memberRole: Role = {
    id: 'member-role',
    name: 'Member',
    scope: Scope.DATA_PRODUCT,
    description: '',
    permissions: [],
    prototype: Prototype.CUSTOM,
};
const ownerRole: Role = { ...memberRole, id: 'owner-role', name: 'Owner', prototype: Prototype.OWNER };
const editorRole: Role = { ...memberRole, id: 'editor-role', name: 'Editor' };
const currentIdentity: Identity = { ...mockUsers[0], type: 'user' };

function assignment(
    identity: Identity,
    overrides: Partial<DataProductRoleAssignmentResponse> = {},
): DataProductRoleAssignmentResponse {
    return {
        id: `assignment-${identity.id}`,
        data_product: mockDataProducts[0],
        identity,
        role: memberRole,
        decision: DecisionStatus.Approved,
        requested_on: '2026-11-16T10:00:00',
        requested_by: mockUsers[0],
        decided_on: null,
        decided_by: null,
        ...overrides,
    };
}

function mockRoles(assignments = [assignment(currentIdentity, { role: ownerRole })]) {
    const state = { assignments };
    allowAllAuth();
    mockIdentitiesHttp();
    server.use(
        http.get(endpoint, () => HttpResponse.json({ role_assignments: state.assignments })),
        http.get('*/api/v2/authz/roles/data_product', () =>
            HttpResponse.json({ roles: [memberRole, ownerRole, editorRole] }),
        ),
    );
    return state;
}

async function findRow(text: string) {
    const row = (await screen.findByText(text)).closest('tr');
    if (!row) throw new Error(`No row contains ${text}`);
    return within(row);
}

async function selectRole(user: ReturnType<typeof userEvent.setup>, label: string, role: string) {
    await user.click(screen.getByLabelText(label, { selector: 'input' }));
    await user.click(await screen.findByText(role, { selector: '.ant-select-item-option-content' }));
}

describe('Data Product identity roles', () => {
    it.each(['team', 'owners'])('keeps surname-first ordering and first-name-first labels in %s', async (view) => {
        const identities: Identity[] = [
            { ...currentIdentity, id: 'alice', first_name: 'Alice', last_name: 'Zulu' },
            { ...currentIdentity, id: 'charlie', first_name: 'Charlie', last_name: 'Adams' },
            { ...currentIdentity, id: 'bob', first_name: 'Bob', last_name: 'Adams' },
            mockGroup,
            mockMachineUser,
        ];
        if (view === 'team') {
            mockRoles(identities.map((identity) => assignment(identity)));
            renderWithProviders(<TeamTab dataProductId="dp-1" />);
        } else {
            renderWithProviders(<IdentityAccessOverview identities={identities} title="Owners" />);
        }

        const names = await screen.findAllByText(/^(Alice Zulu|Charlie Adams|Bob Adams|Finance Team|ETL Runner)$/);
        expect(names.map((name) => name.textContent)).toEqual([
            'Bob Adams',
            'Charlie Adams',
            'ETL Runner',
            'Finance Team',
            'Alice Zulu',
        ]);
    });

    it('shows all identities and counts owners independently of the search', async () => {
        mockRoles([
            assignment(currentIdentity, { role: ownerRole }),
            assignment(mockGroup, { role: ownerRole }),
            assignment(mockMachineUser),
        ]);
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);

        expect((await findRow('Finance Team')).getByText('Group')).toBeInTheDocument();
        expect((await findRow('ETL Runner')).getByText('Machine User')).toBeInTheDocument();
        expect((await findRow('Alice Smith')).getByText('alice@example.com')).toBeInTheDocument();
        await user.type(screen.getByPlaceholderText('Search by name, email, or external ID'), 'TEAM-FINANCE-EXTERNAL');
        expect(screen.queryByText('Alice Smith')).not.toBeInTheDocument();
        expect(screen.getByLabelText('Role for Finance Team')).toBeEnabled();
        expect((await findRow('Finance Team')).getByText('Remove').closest('button')).toBeEnabled();
    });

    it.each([
        {
            column: 'Type',
            ascending: ['Finance Team', 'ETL Runner', 'Bob Adams', 'Charlie Adams', 'Alice Zulu'],
            descending: ['Bob Adams', 'Charlie Adams', 'Alice Zulu', 'ETL Runner', 'Finance Team'],
        },
        {
            column: 'Role',
            ascending: ['Charlie Adams', 'Finance Team', 'Bob Adams', 'ETL Runner', 'Alice Zulu'],
            descending: ['Bob Adams', 'ETL Runner', 'Alice Zulu', 'Charlie Adams', 'Finance Team'],
        },
        {
            column: 'Status',
            ascending: ['Charlie Adams', 'ETL Runner', 'Alice Zulu', 'Bob Adams', 'Finance Team'],
            descending: ['Bob Adams', 'Finance Team', 'Charlie Adams', 'ETL Runner', 'Alice Zulu'],
        },
    ])('cycles $column sorting while keeping Name active', async ({ column, ascending, descending }) => {
        mockRoles([
            assignment({ ...currentIdentity, id: 'alice', first_name: 'Alice', last_name: 'Zulu' }),
            assignment(
                { ...currentIdentity, id: 'bob', first_name: 'Bob', last_name: 'Adams' },
                { decision: DecisionStatus.Pending },
            ),
            assignment(
                { ...currentIdentity, id: 'charlie', first_name: 'Charlie', last_name: 'Adams' },
                { role: editorRole },
            ),
            assignment(mockGroup, { role: editorRole, decision: DecisionStatus.Pending }),
            assignment(mockMachineUser),
        ]);
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await screen.findByText('Alice Zulu');
        const names = () =>
            screen
                .getAllByText(/^(Alice Zulu|Bob Adams|Charlie Adams|Finance Team|ETL Runner)$/)
                .map((name) => name.textContent);
        const nameOrder = ['Bob Adams', 'Charlie Adams', 'ETL Runner', 'Finance Team', 'Alice Zulu'];
        const nameHeader = screen.getByText('Name', { selector: 'th .ant-table-column-title' });
        const header = screen.getByText(column, { selector: 'th .ant-table-column-title' });
        expect(names()).toEqual(nameOrder);
        await user.click(header);
        expect(names()).toEqual(ascending);
        expect(nameHeader.closest('th')).toHaveAttribute('aria-sort', 'ascending');
        await user.click(header);
        expect(names()).toEqual(descending);
        await user.click(header);
        expect(header.closest('th')).not.toHaveAttribute('aria-sort');
        expect(names()).toEqual(nameOrder);
        await user.click(nameHeader);
        expect(names()).toEqual([...nameOrder].reverse());
        await user.click(nameHeader);
        expect(nameHeader.closest('th')).toHaveAttribute('aria-sort', 'ascending');
        await user.click(header);
        expect(names()).toEqual(ascending);
    });

    it('combines Type, Role and Status ordering with Name as the final tie-breaker', async () => {
        mockRoles([
            assignment({ ...currentIdentity, id: 'alice', first_name: 'Alice', last_name: 'Zulu' }),
            assignment(
                { ...currentIdentity, id: 'bob', first_name: 'Bob', last_name: 'Adams' },
                { decision: DecisionStatus.Pending },
            ),
            assignment(
                { ...currentIdentity, id: 'charlie', first_name: 'Charlie', last_name: 'Adams' },
                { role: editorRole },
            ),
            assignment({ ...currentIdentity, id: 'dana', first_name: 'Dana', last_name: 'Smith' }),
            assignment(mockGroup),
        ]);
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await screen.findByText('Alice Zulu');
        for (const column of ['Type', 'Role', 'Status']) {
            await user.click(screen.getByText(column, { selector: 'th .ant-table-column-title' }));
        }
        const names = () =>
            screen
                .getAllByText(/^(Alice Zulu|Bob Adams|Charlie Adams|Dana Smith|Finance Team)$/)
                .map((name) => name.textContent);
        expect(names()).toEqual(['Finance Team', 'Charlie Adams', 'Dana Smith', 'Alice Zulu', 'Bob Adams']);
        await user.click(screen.getByText('Name', { selector: 'th .ant-table-column-title' }));
        expect(names()).toEqual(['Finance Team', 'Charlie Adams', 'Alice Zulu', 'Dana Smith', 'Bob Adams']);
    });

    it('disables assignment controls until the mutation and assignment refresh finish', async () => {
        const state = mockRoles();
        let finishMutation!: () => void;
        let finishRefresh!: () => void;
        const mutation = new Promise<void>((resolve) => {
            finishMutation = resolve;
        });
        const refresh = new Promise<void>((resolve) => {
            finishRefresh = resolve;
        });
        let saved = false;
        const refreshing = vi.fn();
        server.use(
            http.post(endpoint, async () => {
                await mutation;
                const created = assignment(mockGroup);
                state.assignments.push(created);
                saved = true;
                return HttpResponse.json(created);
            }),
            http.get(endpoint, async () => {
                if (saved) {
                    refreshing();
                    await refresh;
                }
                return HttpResponse.json({ role_assignments: state.assignments });
            }),
        );
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await findRow('Alice Smith');
        await user.click(screen.getByText('Add team member'));
        await screen.findByLabelText('Assign role to Finance Team');
        try {
            await selectRole(user, 'Assign role to Finance Team', 'Member');
            expect(screen.getByLabelText('Assign role to Finance Team')).toBeDisabled();
            expect(screen.getByLabelText('Assign role to ETL Runner')).toBeDisabled();
            expect(screen.getByLabelText('Search identities')).toBeDisabled();
            finishMutation();
            await waitFor(() => expect(refreshing).toHaveBeenCalled());
            expect(screen.getByLabelText('Assign role to Finance Team')).toBeDisabled();
            expect(screen.getByLabelText('Assign role to ETL Runner')).toBeDisabled();
            finishRefresh();
            await waitFor(() => expect(screen.queryByLabelText('Assign role to Finance Team')).not.toBeInTheDocument());
            expect(screen.getByLabelText('Assign role to ETL Runner')).toBeEnabled();
        } finally {
            finishMutation();
            finishRefresh();
        }
    });

    it.each([mockGroup, mockMachineUser])(
        'protects the last approved $type owner when another owner is pending',
        async (identity) => {
            mockRoles([
                assignment(identity, { role: ownerRole }),
                assignment(currentIdentity, { role: ownerRole, decision: DecisionStatus.Pending }),
            ]);
            renderWithProviders(<TeamTab dataProductId="dp-1" />);

            const row = await findRow(identity.display_name);
            expect(screen.getByLabelText(`Role for ${identity.display_name}`)).toBeDisabled();
            expect(row.getByText('Remove').closest('button')).toBeDisabled();
        },
    );

    it.each([mockGroup, mockMachineUser])('assigns, changes and removes a $type role', async (identity) => {
        const state = mockRoles();
        const create = vi.fn();
        const modify = vi.fn();
        const remove = vi.fn();
        server.use(
            http.post(endpoint, async ({ request }) => {
                create(await request.json());
                const created = assignment(identity);
                state.assignments.push(created);
                return HttpResponse.json(created);
            }),
            http.put(`${endpoint}/:id`, async ({ request, params }) => {
                modify(params.id, await request.json());
                const updated = assignment(identity, { role: editorRole });
                state.assignments = state.assignments.map((item) => (item.id === updated.id ? updated : item));
                return HttpResponse.json(updated);
            }),
            http.delete(`${endpoint}/:id`, ({ params }) => {
                remove(params.id);
                state.assignments = state.assignments.filter((item) => item.id !== params.id);
                return HttpResponse.json({});
            }),
        );
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await findRow('Alice Smith');
        await user.type(screen.getByPlaceholderText('Search by name, email, or external ID'), identity.display_name);
        await user.click(screen.getByText('Add team member'));
        await screen.findByLabelText(`Assign role to ${identity.display_name}`);
        expect(create).not.toHaveBeenCalled();
        await selectRole(user, `Assign role to ${identity.display_name}`, 'Member');

        await waitFor(() =>
            expect(create).toHaveBeenCalledExactlyOnceWith({
                data_product_id: 'dp-1',
                identity_id: identity.id,
                role_id: memberRole.id,
            }),
        );
        await waitFor(() =>
            expect(screen.queryByLabelText(`Assign role to ${identity.display_name}`)).not.toBeInTheDocument(),
        );
        await user.click(screen.getByText('Cancel'));
        await findRow(identity.display_name);
        await user.click(screen.getByLabelText(`Role for ${identity.display_name}`, { selector: 'input' }));
        const ownerOption = await screen.findByText('Owner', { selector: '.ant-select-item-option-content span' });
        expect(ownerOption.closest('.ant-select-item-option')).toHaveClass('ant-select-item-option-disabled');
        await user.click(await screen.findByText('Editor', { selector: '.ant-select-item-option-content' }));
        await waitFor(() =>
            expect(modify).toHaveBeenCalledExactlyOnceWith(`assignment-${identity.id}`, { role_id: editorRole.id }),
        );
        await waitFor(() => expect(screen.getByLabelText(`Role for ${identity.display_name}`)).toBeEnabled());
        await user.click((await findRow(identity.display_name)).getByText('Remove'));
        await user.click(await screen.findByText('Confirm'));

        await waitFor(() => expect(remove).toHaveBeenCalledExactlyOnceWith(`assignment-${identity.id}`));
        await waitFor(() => expect(screen.queryByText(identity.display_name)).not.toBeInTheDocument());
    });

    it('assigns different roles to multiple identities without closing the modal', async () => {
        const state = mockRoles([]);
        const create = vi.fn();
        server.use(
            http.post(endpoint, async ({ request }) => {
                const body = await request.json();
                create(body);
                const created =
                    create.mock.calls.length === 1
                        ? assignment(currentIdentity, { role: ownerRole })
                        : assignment(mockGroup, { role: editorRole });
                state.assignments.push(created);
                return HttpResponse.json(created);
            }),
        );
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await waitFor(() => expect(screen.getByText('Add team member').closest('button')).toBeEnabled());
        await user.click(screen.getByText('Add team member'));
        await screen.findByLabelText('Assign role to Alice Smith');
        expect(screen.queryByText('Assign role', { exact: true })).not.toBeInTheDocument();
        await selectRole(user, 'Assign role to Alice Smith', 'Owner');
        await waitFor(() => expect(screen.queryByLabelText('Assign role to Alice Smith')).not.toBeInTheDocument());
        await waitFor(() => expect(screen.getByLabelText('Assign role to Finance Team')).toBeEnabled());
        await selectRole(user, 'Assign role to Finance Team', 'Editor');
        await waitFor(() => expect(screen.queryByLabelText('Assign role to Finance Team')).not.toBeInTheDocument());
        expect(create.mock.calls).toEqual([
            [{ data_product_id: 'dp-1', identity_id: currentIdentity.id, role_id: ownerRole.id }],
            [{ data_product_id: 'dp-1', identity_id: mockGroup.id, role_id: editorRole.id }],
        ]);
        expect(screen.getByLabelText('Assign role to ETL Runner')).toBeInTheDocument();
        expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    it.each([mockGroup, mockMachineUser])('disables Owner for a $type and explains why on hover', async (identity) => {
        mockRoles([]);
        const create = vi.fn();
        server.use(
            http.post(endpoint, async ({ request }) => {
                create(await request.json());
                return HttpResponse.json(assignment(identity));
            }),
        );
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await waitFor(() => expect(screen.getByText('Add team member').closest('button')).toBeEnabled());
        await user.click(screen.getByText('Add team member'));
        await user.click(await screen.findByLabelText(`Assign role to ${identity.display_name}`));
        const ownerOption = await screen.findByText('Owner', { selector: '.ant-select-item-option-content span' });
        expect(ownerOption.closest('.ant-select-item-option')).toHaveClass('ant-select-item-option-disabled');
        expect(screen.queryByText('Only users can be Data Product owners')).not.toBeInTheDocument();
        await user.hover(ownerOption);
        expect(await screen.findByText('Only users can be Data Product owners')).toBeInTheDocument();
        await user.click(ownerOption);
        expect(create).not.toHaveBeenCalled();
        await user.click(await screen.findByText('Member', { selector: '.ant-select-item-option-content' }));

        await waitFor(() =>
            expect(create).toHaveBeenCalledExactlyOnceWith({
                data_product_id: 'dp-1',
                identity_id: identity.id,
                role_id: memberRole.id,
            }),
        );
    });

    it('hides approved and pending identities even when the team search hides them, but permits retrying denied requests', async () => {
        mockRoles([
            assignment(currentIdentity, { role: ownerRole }),
            assignment(mockGroup, { decision: DecisionStatus.Pending }),
            assignment(mockMachineUser, { decision: DecisionStatus.Denied }),
        ]);
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await findRow('Alice Smith');
        await user.type(screen.getByPlaceholderText('Search by name, email, or external ID'), 'nobody');
        await user.click(screen.getByText('Add team member'));

        expect(await screen.findByLabelText('Assign role to ETL Runner')).toBeEnabled();
        expect(screen.queryByLabelText('Assign role to Alice Smith')).not.toBeInTheDocument();
        expect(screen.queryByLabelText('Assign role to Finance Team')).not.toBeInTheDocument();
    });

    it('lets an approved identity receive a replacement when its role has been deleted', async () => {
        const state = mockRoles([
            assignment(currentIdentity, { role: ownerRole }),
            assignment(mockGroup, { role: null }),
        ]);
        const modify = vi.fn();
        server.use(
            http.put(`${endpoint}/:id`, async ({ request, params }) => {
                modify(params.id, await request.json());
                const updated = assignment(mockGroup);
                state.assignments = state.assignments.map((item) => (item.id === updated.id ? updated : item));
                return HttpResponse.json(updated);
            }),
        );
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        expect((await findRow('Finance Team')).getByText('No role assigned')).toBeInTheDocument();
        await selectRole(user, 'Role for Finance Team', 'Member');

        await waitFor(() =>
            expect(modify).toHaveBeenCalledExactlyOnceWith('assignment-group-1', { role_id: memberRole.id }),
        );
        await waitFor(() =>
            expect(screen.getByLabelText('Role for Finance Team').closest('.ant-select')).toHaveTextContent('Member'),
        );
    });

    it('keeps the saved role displayed when a change fails', async () => {
        mockRoles([assignment(currentIdentity, { role: ownerRole }), assignment(mockGroup)]);
        server.use(http.put(`${endpoint}/:id`, () => HttpResponse.json({ detail: 'Update failed' }, { status: 500 })));
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await findRow('Finance Team');
        await selectRole(user, 'Role for Finance Team', 'Editor');

        await screen.findByText('Failed to update Data Product role');
        expect((await findRow('Finance Team')).getByText('Member')).toBeInTheDocument();
    });

    it('keeps an identity available for retry after a failed assignment', async () => {
        const state = mockRoles();
        server.use(http.post(endpoint, () => HttpResponse.json({ detail: 'Assignment failed' }, { status: 500 })));
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await findRow('Alice Smith');
        await user.click(screen.getByText('Add team member'));
        await screen.findByLabelText('Assign role to Finance Team');
        await selectRole(user, 'Assign role to Finance Team', 'Member');

        await screen.findByText('Failed to assign role');
        expect(screen.getByText('Finance Team')).toBeInTheDocument();
        await waitFor(() => expect(screen.getByLabelText('Assign role to Finance Team')).toBeEnabled());
        server.use(
            http.post(endpoint, () => {
                const created = assignment(mockGroup);
                state.assignments.push(created);
                return HttpResponse.json(created);
            }),
        );
        await selectRole(user, 'Assign role to Finance Team', 'Member');
        await waitFor(() => expect(screen.queryByLabelText('Assign role to Finance Team')).not.toBeInTheDocument());
    });

    it('does not offer requests from the Team tab when the user cannot assign roles', async () => {
        mockRoles();
        server.use(
            http.get('*/api/v2/authz/access/:action', ({ params }) =>
                HttpResponse.json({
                    allowed: params.action !== String(AuthorizationAction.DATA_PRODUCT__CREATE_USER),
                }),
            ),
        );
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await findRow('Alice Smith');

        expect(screen.getByText('Add team member').closest('button')).toBeDisabled();
        expect(screen.queryByText('Request role')).not.toBeInTheDocument();
    });

    it('disables role changes and removals while a mutation is in flight', async () => {
        const state = mockRoles([
            assignment(currentIdentity, { role: ownerRole }),
            assignment(mockGroup),
            assignment(mockMachineUser),
        ]);
        let resolveRequest!: () => void;
        const pending = new Promise<void>((resolve) => {
            resolveRequest = resolve;
        });
        server.use(
            http.put(`${endpoint}/:id`, async () => {
                await pending;
                const updated = assignment(mockGroup, { role: editorRole });
                state.assignments = state.assignments.map((item) => (item.id === updated.id ? updated : item));
                return HttpResponse.json(updated);
            }),
        );
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await findRow('Finance Team');
        try {
            await selectRole(user, 'Role for Finance Team', 'Editor');
            await waitFor(() => expect(screen.getByLabelText('Role for Finance Team')).toBeDisabled());
            expect(screen.getByLabelText('Role for ETL Runner')).toBeDisabled();
            expect((await findRow('ETL Runner')).getByText('Remove').closest('button')).toBeDisabled();
            resolveRequest();
            await waitFor(() => expect(screen.getByLabelText('Role for ETL Runner')).toBeEnabled());
        } finally {
            resolveRequest();
        }
    });

    it('requests a role only for the current user without offering identity selection', async () => {
        mockRoles([]);
        const loadDirectory = vi.fn(() => HttpResponse.json({ users: mockUsers }));
        const requestRole = vi.fn();
        server.use(
            http.get('*/api/v2/users', loadDirectory),
            http.post(`${endpoint}/request`, async ({ request }) => {
                requestRole(await request.json());
                return HttpResponse.json(assignment(currentIdentity, { decision: DecisionStatus.Pending }));
            }),
        );
        const user = userEvent.setup();
        renderWithProviders(<DataProductRequestAccessButton dataProductId="dp-1" user={mockUsers[0]} />);
        await user.click(screen.getByText('Join Team'));

        expect(await screen.findByText('Alice Smith')).toBeInTheDocument();
        expect(screen.queryByText('Change identity')).not.toBeInTheDocument();
        expect(screen.queryByText('Request role', { exact: true })).not.toBeInTheDocument();
        await selectRole(user, 'Role', 'Member');

        await waitFor(() =>
            expect(requestRole).toHaveBeenCalledExactlyOnceWith({
                data_product_id: 'dp-1',
                identity_id: currentIdentity.id,
                role_id: memberRole.id,
            }),
        );
        expect(loadDirectory).not.toHaveBeenCalled();
    });

    it('disables the inline request selector while submitting and allows retrying the same role after failure', async () => {
        mockRoles([]);
        let finishRequest!: () => void;
        const pending = new Promise<void>((resolve) => {
            finishRequest = resolve;
        });
        const requestRole = vi.fn();
        server.use(
            http.post(`${endpoint}/request`, async ({ request }) => {
                requestRole(await request.json());
                await pending;
                return HttpResponse.json({ detail: 'Request failed' }, { status: 500 });
            }),
        );
        const user = userEvent.setup();
        renderWithProviders(<DataProductRequestAccessButton dataProductId="dp-1" user={mockUsers[0]} />);
        await user.click(screen.getByText('Join Team'));
        await screen.findByText('Alice Smith');
        try {
            await selectRole(user, 'Role', 'Member');
            expect(screen.getByLabelText('Role')).toBeDisabled();
            finishRequest();
            await screen.findByText('Failed to request role');
            await waitFor(() => expect(screen.getByLabelText('Role')).toBeEnabled());
            server.use(
                http.post(`${endpoint}/request`, async ({ request }) => {
                    requestRole(await request.json());
                    return HttpResponse.json(assignment(currentIdentity, { decision: DecisionStatus.Pending }));
                }),
            );
            await selectRole(user, 'Role', 'Member');
            await waitFor(() => expect(screen.queryByLabelText('Role')).not.toBeInTheDocument());
            expect(requestRole).toHaveBeenCalledTimes(2);
            expect(requestRole).toHaveBeenLastCalledWith({
                data_product_id: 'dp-1',
                identity_id: currentIdentity.id,
                role_id: memberRole.id,
            });
        } finally {
            finishRequest();
        }
    });

    describe.each([mockGroup, mockMachineUser])('$type pending requests', (identity) => {
        it.each([DecisionStatus.Approved, DecisionStatus.Denied])(
            'persists a %s decision from Pending requests',
            async (decision) => {
                const pending = assignment(identity, { decision: DecisionStatus.Pending });
                const state = mockRoles([pending]);
                const decide = vi.fn();
                server.use(
                    http.get('*/api/v2/users/current/pending_actions', () =>
                        HttpResponse.json({
                            pending_actions: state.assignments
                                .filter((item) => item.decision === DecisionStatus.Pending)
                                .map((item) => ({ ...item, request_type: RequestType_DataProductRoleAssignment })),
                        }),
                    ),
                    http.post(`${endpoint}/:id/decide`, async ({ request, params }) => {
                        decide(params.id, await request.json());
                        pending.decision = decision;
                        return HttpResponse.json(pending);
                    }),
                );
                const user = userEvent.setup();
                renderWithProviders(<PendingAccessRequestsTab />, { routerProps: {} });
                const row = await findRow(`${identity.display_name} requests the Member role for Sales Analytics`);
                await user.click(row.getByText('Review'));
                expect(screen.getByText(identity.display_name)).toBeInTheDocument();
                expect(screen.getByText(identity.type === 'group' ? 'Group' : 'Machine User')).toBeInTheDocument();
                await user.click(screen.getByText(decision === DecisionStatus.Approved ? 'Accept' : 'Decline'));

                await waitFor(() => expect(decide).toHaveBeenCalledExactlyOnceWith(pending.id, { decision }));
                expect(await screen.findByText('Nothing to review')).toBeInTheDocument();
            },
        );
    });
});
