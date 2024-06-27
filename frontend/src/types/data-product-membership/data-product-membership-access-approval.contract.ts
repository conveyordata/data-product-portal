import { DataProductMembershipContract } from '@/types/data-product-membership/data-product-membership.contract.ts';

export interface DataProductMembershipApprovalRequest {
    membershipId: string;
}

export interface DataProductMembershipApprovalResponse extends DataProductMembershipContract {}
