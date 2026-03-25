import { HttpResponse, http } from 'msw';
import type { GetUsersResponse, UsersGet } from '@/store/api/services/generated/usersApi';
import { server } from '@/tests/mocks/server.ts';

export const mockUsers: UsersGet[] = [
    {
        id: '1',
        email: 'alice@example.com',
        external_id: 'ext-1',
        first_name: 'Alice',
        last_name: 'Smith',
        has_seen_tour: true,
        can_become_admin: false,
        global_role: null,
    },
    {
        id: '2',
        email: 'bob@example.com',
        external_id: 'ext-2',
        first_name: 'Bob',
        last_name: 'Jones',
        has_seen_tour: false,
        can_become_admin: true,
        global_role: null,
    },
];

export const mockUsersHttp = (users: UsersGet[]) => {
    server.use(
        http.get('*/api/v2/users', () => {
            return HttpResponse.json({ users } satisfies GetUsersResponse);
        }),
    );
};
