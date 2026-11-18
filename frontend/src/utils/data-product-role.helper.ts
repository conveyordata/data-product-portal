import { useListDataProductRoleAssignmentsQuery } from '@/store/api/services/generated/authorizationRoleAssignmentsApi.ts';
import { DecisionStatus, Prototype } from '@/types/roles';
import type { Identity } from '@/utils/identity.ts';

export function useGetDataProductOwners(dataProductId: string | undefined): Identity[] | undefined {
    const { data: roleAssignments } = useListDataProductRoleAssignmentsQuery(
        {
            dataProductId,
            decision: DecisionStatus.Approved,
        },
        { skip: !dataProductId },
    );

    return roleAssignments?.role_assignments
        .filter((assignment) => assignment.role?.prototype === Prototype.OWNER)
        .map((assignment) => assignment.identity);
}

export function useGetDataProductOwnerIds(dataProductId: string | undefined): string[] | undefined {
    return useGetDataProductOwners(dataProductId)?.map((owner) => owner.id);
}
