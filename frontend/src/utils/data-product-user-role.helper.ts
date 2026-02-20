import { useListDataProductRoleAssignmentsQuery } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import { DecisionStatus, Prototype } from '@/types/roles';
import type { UserContract } from '@/types/users/user.contract.ts';

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
