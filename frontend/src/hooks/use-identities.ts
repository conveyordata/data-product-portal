import { useMemo } from 'react';
import { useGetGroupsQuery } from '@/store/api/services/generated/groupsApi.ts';
import { useGetMachineUsersQuery } from '@/store/api/services/generated/machineUsersApi.ts';
import { useGetUsersQuery } from '@/store/api/services/generated/usersApi.ts';
import type { Identity } from '@/utils/identity.ts';

export function useIdentities(options: { skip?: boolean } = {}) {
    const users = useGetUsersQuery(undefined, options);
    const groups = useGetGroupsQuery(undefined, options);
    const machineUsers = useGetMachineUsersQuery(undefined, options);

    const currentData = useMemo<Identity[] | undefined>(() => {
        if (!users.currentData || !groups.currentData || !machineUsers.currentData) {
            return undefined;
        }

        return [
            ...users.currentData.users.map((user): Identity => ({ ...user, type: 'user' })),
            ...groups.currentData.groups.map((group): Identity => ({ ...group, type: 'group' })),
            ...machineUsers.currentData.machine_users.map(
                (machineUser): Identity => ({ ...machineUser, type: 'machine_user' }),
            ),
        ];
    }, [users.currentData, groups.currentData, machineUsers.currentData]);

    return {
        currentData,
        isFetching: users.isFetching || groups.isFetching || machineUsers.isFetching,
        isUninitialized: users.isUninitialized || groups.isUninitialized || machineUsers.isUninitialized,
        isError: users.isError || groups.isError || machineUsers.isError,
        refetch: () => Promise.all([users.refetch(), groups.refetch(), machineUsers.refetch()]),
    };
}
