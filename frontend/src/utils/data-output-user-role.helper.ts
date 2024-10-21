import { DataOutputContract } from '@/types/data-output';
import {
    DataProductMembershipRole,
    DataProductMembershipRoleType,
} from '@/types/data-product-membership';

export function getDataOutputUserRole(
    dataOutput: DataOutputContract,
    userId: string,
): DataProductMembershipRoleType {
    return (
        dataOutput?.owner.memberships?.find((membership) => membership?.user_id === userId)?.role ||
        DataProductMembershipRole.NonMember
    );
}

export function getIsDataOutputOwner(dataOutput: DataOutputContract, userId: string): boolean {
    return getDataOutputUserRole(dataOutput, userId) === DataProductMembershipRole.Owner;
}
