import { useListOutputPortRoleAssignmentsQuery } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import { DecisionStatus, Prototype } from '@/types/roles';
import type { UserContract } from '@/types/users/user.contract.ts';

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
