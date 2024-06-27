export enum DataProductMembershipRole {
    Owner = 'owner',
    Member = 'member',
    NonMember = 'non-member',
}

export type DataProductMembershipRoleType =
    | DataProductMembershipRole.Member
    | DataProductMembershipRole.Owner
    | DataProductMembershipRole.NonMember;
