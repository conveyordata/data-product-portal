import { useGetDataProductRoleAssignmentsQuery } from '@/store/features/role-assignments/data-product-roles-api-slice';
import { DecisionStatus } from '@/types/roles';
import { Prototype } from '@/types/roles/role.contract';
import type { UserContract } from '@/types/users';

export function useGetDataProductOwners(dataProductId: string | undefined): UserContract[] | undefined {
    const { data: roleAssignments } = useGetDataProductRoleAssignmentsQuery(
        {
            data_product_id: dataProductId!,
            decision: DecisionStatus.Approved,
        },
        { skip: !dataProductId },
    );

    return roleAssignments
        ?.filter((assignment) => assignment.role.prototype === Prototype.OWNER)
        .map((assignment) => assignment.user);
}

export function useGetDataProductOwnerIds(dataProductId: string | undefined): string[] | undefined {
    const owners = useGetDataProductOwners(dataProductId);
    return owners?.map((owner) => owner.id);
}
