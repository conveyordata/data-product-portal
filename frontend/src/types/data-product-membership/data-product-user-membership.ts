import { DataProductMembershipContract } from '@/types/data-product-membership/data-product-membership.contract.ts';

export type DataProductUserMembership = Pick<DataProductMembershipContract, 'user' | 'role' | 'id' | 'status'>;
