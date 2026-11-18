import { HttpResponse, http } from 'msw';
import type {
    GroupIdentity,
    MachineUserIdentity,
} from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import type { GroupsGetResponse } from '@/store/api/services/generated/groupsApi.ts';
import type { MachineUsersGetResponse } from '@/store/api/services/generated/machineUsersApi.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockUsers, mockUsersHttp } from '@/tests/mocks/users.ts';

export const mockGroup: GroupIdentity = {
    id: 'group-1',
    type: 'group',
    display_name: 'Finance Team',
    external_id: 'team-finance-external',
};

export const mockMachineUser: MachineUserIdentity = {
    id: 'machine-1',
    type: 'machine_user',
    display_name: 'ETL Runner',
    external_id: 'service-principal-id',
};

export function mockIdentitiesHttp() {
    mockUsersHttp(mockUsers);
    server.use(
        http.get('*/api/v2/groups', () =>
            HttpResponse.json({
                groups: [
                    { id: mockGroup.id, display_name: mockGroup.display_name, external_id: mockGroup.external_id },
                ],
            } satisfies GroupsGetResponse),
        ),
        http.get('*/api/v2/machine-users', () =>
            HttpResponse.json({
                machine_users: [
                    {
                        id: mockMachineUser.id,
                        display_name: mockMachineUser.display_name,
                        external_id: mockMachineUser.external_id,
                    },
                ],
            } satisfies MachineUsersGetResponse),
        ),
    );
}
