import { DatasetMembershipContract } from '@/types/dataset-membership/dataset-membership.contract.ts';

export interface DatasetMembershipApprovalRequest {
    membershipId: string;
}

export interface DatasetMembershipApprovalResponse extends DatasetMembershipContract {}
