import { useGetRoleAssignmentQuery } from '@/store/features/role-assignments/dataset-roles-api-slice.ts';
import { DecisionStatus } from '@/types/roles';
import { Prototype } from '@/types/roles/role.contract.ts';
import type { UserContract } from '@/types/users';

export function useGetDatasetOwners(datasetId: string | undefined): UserContract[] {
    const { data: roleAssignments } = useGetRoleAssignmentQuery(
        {
            dataset_id: datasetId!,
            decision: DecisionStatus.Approved,
        },
        { skip: !datasetId },
    );

    return (roleAssignments ?? [])
        .filter((assignment) => assignment.role.prototype === Prototype.OWNER)
        .map((assignment) => assignment.user);
}

export function useGetDatasetOwnerIds(datasetId: string | undefined): string[] {
    const owners = useGetDatasetOwners(datasetId);
    return owners.map((owner) => owner.id);
}
