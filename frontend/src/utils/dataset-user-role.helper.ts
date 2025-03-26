import { DatasetContract } from '@/types/dataset';
import {
    DatasetMembershipRole,
    DatasetMembershipRoleType,
    DatasetMembershipStatus,
    DatasetUserMembership,
} from '@/types/dataset-membership';

export function getDatasetUserRole(dataset: DatasetContract, userId: string): DatasetMembershipRoleType {
    return (
        dataset?.memberships?.find((membership) => membership?.user_id === userId)?.role ||
        DatasetMembershipRole.NonMember
    );
}

export function getDatasetOwners(dataset: DatasetContract) {
    return (
        dataset?.memberships
            ?.filter((membership) => membership.role === DatasetMembershipRole.Owner)
            .map((membership) => membership.user) || []
    );
}

// export function getDatasetMembers(dataset: DatasetContract) {
//     return (
//         dataset?.memberships
//             ?.filter((membership) => membership.role === DatasetMembershipRole.Member)
//             .map((membership) => membership.user) || []
//     );
// }

// export function getDatasetMemberMemberships(dataset: DatasetContract) {
//     return dataset?.memberships?.filter((membership) => membership.role === DatasetMembershipRole.Member) || [];
// }

export function getIsDatasetOwner(dataset: DatasetContract, userId: string): boolean {
    return getDatasetUserRole(dataset, userId) === DatasetMembershipRole.Owner;
}

// export function getIsDatasetMember(dataset: DatasetContract, userId: string): boolean {
//     return getDatasetUserRole(dataset, userId) === DatasetMembershipRole.Member;
// }

export function getIsUserDatasetOwner(userId: string, datasetUsers: DatasetUserMembership[]) {
    return datasetUsers.some((user) => user.user.id === userId && user.role === DatasetMembershipRole.Owner);
}

export function getCanUserAccessDatasetData(userId: string, datasetUsers: DatasetUserMembership[]) {
    return datasetUsers.some((user) => user.user.id === userId && user.status === DatasetMembershipStatus.Approved);
}

export function getDoesUserHaveAnyDatasetMembership(userId: string, datasetUsers: DatasetUserMembership[]) {
    return datasetUsers.some((user) => user.user.id === userId);
}

export function getDatasetOwnerIds(dataset: DatasetContract) {
    return getDatasetOwners(dataset).map((owner) => owner.id);
}
