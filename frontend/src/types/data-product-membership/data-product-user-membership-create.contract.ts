import { DataProductMembershipContract } from '@/types/data-product-membership';

export type DataProductUserMembershipCreateContract = Pick<DataProductMembershipContract, 'user_id' | 'role'>;
