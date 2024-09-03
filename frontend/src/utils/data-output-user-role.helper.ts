// import { DataOutputContract } from '@/types/data-output';
// import { DataProductContract } from '@/types/data-product';
// import {
//     DataProductMembershipRole,
//     DataProductMembershipRoleType,
//     DataProductMembershipStatus,
//     DataProductUserMembership,
// } from '@/types/data-product-membership';

// export function getDataOutputUserRole(
//     dataOutput: DataOutputContract,
//     userId: string,
// ): DataProductMembershipRoleType {
//     return (
//         dataOutput?.owner.memberships?.find((membership) => membership?.user_id === userId)?.role ||
//         DataProductMembershipRole.NonMember
//     );
// }

// export function getDataOutputOwners(dataOutput: DataOutputContract) {
//     return (
//         dataOutput?.owner.memberships
//             ?.filter((membership) => membership.role === DataProductMembershipRole.Owner)
//             .map((membership) => membership.user) || []
//     );
// }

// export function getDataOutputMembers(dataOutput: DataOutputContract) {
//     return (
//         dataOutput.owner?.memberships
//             ?.filter((membership) => membership.role === DataProductMembershipRole.Member)
//             .map((membership) => membership.user) || []
//     );
// }

// export function getDataOutputMemberMemberships(dataOutput: DataOutputContract) {
//     return dataOutput?.owner.memberships?.filter((membership) => membership.role === DataProductMembershipRole.Member) || [];
// }

// export function getIsDataOutputOwner(dataOutput: DataOutputContract, userId: string): boolean {
//     return getDataOutputUserRole(dataOutput, userId) === DataProductMembershipRole.Owner;
// }

// export function getIsDataOutputMember(dataOutput: DataOutputContract, userId: string): boolean {
//     return getDataOutputUserRole(dataOutput, userId) === DataProductMembershipRole.Member;
// }

// // export function getIsUserDataOutputOwner(userId: string, dataProductUsers: DataProductUserMembership[]) {
// //     return dataProductUsers.some((user) => user.user.id === userId && user.role === DataProductMembershipRole.Owner);
// // }

// // export function getCanUserAccessDataProductData(userId: string, dataProductUsers: DataProductUserMembership[]) {
// //     return dataProductUsers.some(
// //         (user) => user.user.id === userId && user.status === DataProductMembershipStatus.Approved,
// //     );
// // }

// // export function getDoesUserHaveAnyDataProductMembership(userId: string, dataProductUsers: DataProductUserMembership[]) {
// //     return dataProductUsers.some((user) => user.user.id === userId);
// // }

// export function getDataOutputOwnerIds(dataOutput: DataOutputContract) {
//     return getDataOutputOwners(dataOutput).map((owner) => owner.id);
// }
