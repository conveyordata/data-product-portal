import { useListOutputPortRoleAssignmentsQuery } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import { DecisionStatus } from '@/types/roles';
import { Prototype } from '@/types/roles/role.contract';
import type { UserContract } from '@/types/users';

export function useGetDatasetOwners(datasetId: string | undefined): UserContract[] | undefined {
    const { data: roleAssignments } = useListOutputPortRoleAssignmentsQuery(
        {
            outputPortId: datasetId,
            decision: DecisionStatus.Approved,
        },
        { skip: !datasetId },
    );

    return roleAssignments?.role_assignments
        ?.filter((assignment) => assignment.role?.prototype === Prototype.OWNER)
        .map((assignment) => assignment.user);
}

export function useGetDatasetOwnerIds(datasetId: string | undefined): string[] | undefined {
    const owners = useGetDatasetOwners(datasetId);
    return owners?.map((owner) => owner.id);
}
