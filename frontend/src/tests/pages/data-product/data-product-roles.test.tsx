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
        await user.click(
            await screen.findByLabelText(
                `Select ${identity.display_name} (${identity.type === 'group' ? 'Group' : 'Machine User'})`,
            ),
        );
        expect(create).not.toHaveBeenCalled();
        await selectRole(user, 'Role', 'Member');
        await user.click(screen.getByText('Assign role'));

        await waitFor(() =>
            expect(create).toHaveBeenCalledExactlyOnceWith({
                data_product_id: 'dp-1',
                identity_id: identity.id,
                role_id: memberRole.id,
            }),
        );
        await waitFor(() => expect(screen.queryByText('Change identity')).not.toBeInTheDocument());
        await findRow(identity.display_name);
        await user.click(screen.getByLabelText(`Role for ${identity.display_name}`, { selector: 'input' }));
        const ownerOption = await screen.findByText('Owner', { selector: '.ant-select-item-option-content' });
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

    it('allows selecting Owner before a user and keeps it when changing users', async () => {
        mockRoles([]);
        const create = vi.fn();
        server.use(
            http.post(endpoint, async ({ request }) => {
                create(await request.json());
                return HttpResponse.json(assignment(currentIdentity, { role: ownerRole }));
            }),
        );
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await waitFor(() => expect(screen.getByText('Add team member').closest('button')).toBeEnabled());
        await user.click(screen.getByText('Add team member'));
        await screen.findByLabelText('Select Finance Team (Group)');
        expect(screen.getByLabelText('Select ETL Runner (Machine User)')).toBeInTheDocument();
        await selectRole(user, 'Role', 'Owner');
        expect(screen.queryByLabelText('Select Finance Team (Group)')).not.toBeInTheDocument();
        expect(screen.queryByLabelText('Select ETL Runner (Machine User)')).not.toBeInTheDocument();
        expect(screen.queryByText('Groups')).not.toBeInTheDocument();
        expect(screen.queryByText('Machine Users')).not.toBeInTheDocument();
        await user.click(await screen.findByLabelText('Select Bob Jones (User)'));
        await user.click(screen.getByText('Change identity'));
        expect(screen.getByText('Owner', { selector: '.ant-select-content' })).toBeInTheDocument();
        await user.click(await screen.findByLabelText('Select Alice Smith (User)'));
        await user.click(screen.getByText('Assign role'));

        await waitFor(() =>
            expect(create).toHaveBeenCalledExactlyOnceWith({
                data_product_id: 'dp-1',
                identity_id: currentIdentity.id,
                role_id: ownerRole.id,
            }),
        );
    });

    it('does not reselect Users or change other role filters when selecting Owner', async () => {
        mockRoles([]);
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await waitFor(() => expect(screen.getByText('Add team member').closest('button')).toBeEnabled());
        await user.click(screen.getByText('Add team member'));
        await screen.findByLabelText('Select Alice Smith (User)');
        await user.click(screen.getByLabelText('Type', { selector: 'input' }));
        await user.click(screen.getByText('Users', { selector: '.ant-select-item-option-content' }));
        await selectRole(user, 'Role', 'Member');
        expect(screen.getByLabelText('Select Finance Team (Group)')).toBeInTheDocument();
        expect(screen.getByLabelText('Select ETL Runner (Machine User)')).toBeInTheDocument();
        expect(screen.queryByLabelText('Select Alice Smith (User)')).not.toBeInTheDocument();

        await selectRole(user, 'Role', 'Owner');
        expect(screen.getByText('No identities match the current filters')).toBeInTheDocument();
        expect(screen.queryByLabelText(/^Select /)).not.toBeInTheDocument();
    });

    it.each([mockGroup, mockMachineUser])(
        'clears and disables the owner role when switching to a $type',
        async (identity) => {
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
            await user.click(await screen.findByLabelText('Select Alice Smith (User)'));
            await selectRole(user, 'Role', 'Owner');
            await user.click(screen.getByText('Change identity'));
            expect(screen.getByText('Owner', { selector: '.ant-select-content' })).toBeInTheDocument();
            await user.click(screen.getByLabelText('Type', { selector: 'input' }));
            await user.click(
                screen.getByText(identity.type === 'group' ? 'Groups' : 'Machine Users', {
                    selector: '.ant-select-item-option-content',
                }),
            );
            await user.click(
                await screen.findByLabelText(
                    `Select ${identity.display_name} (${identity.type === 'group' ? 'Group' : 'Machine User'})`,
                ),
            );
            expect(screen.getByText('Only users can be Data Product owners')).toBeInTheDocument();
            await user.click(screen.getByText('Assign role'));
            expect(await screen.findByText('Please select a role')).toBeInTheDocument();
            expect(create).not.toHaveBeenCalled();

            await user.click(screen.getByLabelText('Role', { selector: 'input' }));
            const ownerOption = await screen.findByText('Owner', { selector: '.ant-select-item-option-content' });
            expect(ownerOption.closest('.ant-select-item-option')).toHaveClass('ant-select-item-option-disabled');
            await user.click(await screen.findByText('Member', { selector: '.ant-select-item-option-content' }));
            await user.click(screen.getByText('Assign role'));

            await waitFor(() =>
                expect(create).toHaveBeenCalledExactlyOnceWith({
                    data_product_id: 'dp-1',
                    identity_id: identity.id,
                    role_id: memberRole.id,
                }),
            );
        },
    );

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

        expect(await screen.findByLabelText('Select ETL Runner (Machine User)')).toBeEnabled();
        expect(screen.queryByLabelText('Select Alice Smith (User)')).not.toBeInTheDocument();
        expect(screen.queryByLabelText('Select Finance Team (Group)')).not.toBeInTheDocument();
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

    it('keeps the selected identity and role available for retry after a failed assignment', async () => {
        mockRoles();
        server.use(http.post(endpoint, () => HttpResponse.json({ detail: 'Assignment failed' }, { status: 500 })));
        const user = userEvent.setup();
        renderWithProviders(<TeamTab dataProductId="dp-1" />);
        await findRow('Alice Smith');
        await user.click(screen.getByText('Add team member'));
        await user.click(await screen.findByLabelText('Select Finance Team (Group)'));
        await selectRole(user, 'Role', 'Member');
        await user.click(screen.getByText('Assign role'));

        await screen.findByText('Failed to assign role');
        expect(screen.getByText('Finance Team')).toBeInTheDocument();
        expect(screen.getByLabelText('Role', { selector: 'input' }).closest('.ant-select')).toHaveTextContent('Member');
        await waitFor(() => expect(screen.getByText('Assign role').closest('button')).toBeEnabled());
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
        await selectRole(user, 'Role', 'Member');
        await user.click(screen.getByText('Request role'));

        await waitFor(() =>
            expect(requestRole).toHaveBeenCalledExactlyOnceWith({
                data_product_id: 'dp-1',
                identity_id: currentIdentity.id,
                role_id: memberRole.id,
            }),
        );
        expect(loadDirectory).not.toHaveBeenCalled();
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
