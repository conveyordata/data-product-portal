import { DataProductMembershipContract } from '@/types/data-product-membership';

export interface DataProductMembershipRequestAccessRequest {
    dataProductId: string;
    userId: string;
}

export type DataProductMembershipRequestAccessResponse = DataProductMembershipContract;
