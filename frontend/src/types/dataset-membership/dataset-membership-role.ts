export enum DatasetMembershipRole {
    Owner = 'owner',
    NonMember = 'non-member',
}

export type DatasetMembershipRoleType = DatasetMembershipRole.Owner | DatasetMembershipRole.NonMember;
