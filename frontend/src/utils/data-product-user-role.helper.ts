import { useListDataProductRoleAssignmentsQuery } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import { DecisionStatus } from '@/types/roles';
import { Prototype } from '@/types/roles/role.contract';
import type { UserContract } from '@/types/users';

export function useGetDataProductOwners(dataProductId: string | undefined): UserContract[] | undefined {
    const { data: roleAssignments } = useListDataProductRoleAssignmentsQuery(
        {
            dataProductId: dataProductId,
            decision: DecisionStatus.Approved,
        },
        { skip: !dataProductId },
    );

    return roleAssignments?.role_assignments
        ?.filter((assignment) => assignment.role?.prototype === Prototype.OWNER)
        .map((assignment) => assignment.user);
}

export function useGetDataProductOwnerIds(dataProductId: string | undefined): string[] | undefined {
    const owners = useGetDataProductOwners(dataProductId);
    return owners?.map((owner) => owner.id);
}
