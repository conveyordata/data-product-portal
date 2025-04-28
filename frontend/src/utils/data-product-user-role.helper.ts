import { DataProductContract } from '@/types/data-product';
import {
    DataProductMembershipRole,
    DataProductMembershipRoleType,
    DataProductUserMembership,
} from '@/types/data-product-membership';
import { DecisionStatus } from '@/types/roles';

export function getDataProductUserRole(
    dataProduct: DataProductContract,
    userId: string,
): DataProductMembershipRoleType {
    return (
        dataProduct?.memberships?.find((membership) => membership?.user_id === userId)?.role ||
        DataProductMembershipRole.NonMember
    );
}

export function getDataProductOwners(dataProduct: DataProductContract) {
    return (
        dataProduct?.memberships
            ?.filter((membership) => membership.role === DataProductMembershipRole.Owner)
            .map((membership) => membership.user) || []
    );
}

export function getDataProductMembers(dataProduct: DataProductContract) {
    return (
        dataProduct?.memberships
            ?.filter((membership) => membership.role === DataProductMembershipRole.Member)
            .map((membership) => membership.user) || []
    );
}

export function getDataProductMemberMemberships(dataProduct: DataProductContract) {
    return dataProduct?.memberships?.filter((membership) => membership.role === DataProductMembershipRole.Member) || [];
}

export function getIsDataProductOwner(dataProduct: DataProductContract, userId: string): boolean {
    return getDataProductUserRole(dataProduct, userId) === DataProductMembershipRole.Owner;
}

export function getIsDataProductMember(dataProduct: DataProductContract, userId: string): boolean {
    return getDataProductUserRole(dataProduct, userId) === DataProductMembershipRole.Member;
}

export function getIsUserDataProductOwner(userId: string, dataProductUsers: DataProductUserMembership[]) {
    return dataProductUsers.some((user) => user.user.id === userId && user.role === DataProductMembershipRole.Owner);
}

export function getCanUserAccessDataProductData(userId: string, dataProductUsers: DataProductUserMembership[]) {
    return dataProductUsers.some((user) => user.user.id === userId && user.status === DecisionStatus.Approved);
}

export function getDoesUserHaveAnyDataProductMembership(userId: string, dataProductUsers: DataProductUserMembership[]) {
    return dataProductUsers.some((user) => user.user.id === userId);
}

export function getDataProductOwnerIds(dataProduct: DataProductContract) {
    return getDataProductOwners(dataProduct).map((owner) => owner.id);
}
