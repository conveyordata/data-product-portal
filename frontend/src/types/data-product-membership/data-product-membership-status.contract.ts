export enum DataProductMembershipStatus {
    Approved = 'approved',
    Pending = 'pending_approval',
    Denied = 'denied',
}

export type DataProductMembershipStatusType =
    | DataProductMembershipStatus.Approved
    | DataProductMembershipStatus.Pending
    | DataProductMembershipStatus.Denied;
