export enum DatasetMembershipStatus {
    Approved = 'approved',
    Pending = 'pending_approval',
    Denied = 'denied',
}

export type DatasetMembershipStatusType =
    | DatasetMembershipStatus.Approved
    | DatasetMembershipStatus.Pending
    | DatasetMembershipStatus.Denied;
