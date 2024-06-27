import { DataProductMembershipRoleType } from '@/types/data-product-membership';

export interface DataProductMembershipRoleUpdateRequest {
    dataProductId: string;
    membershipId: string;
    role: DataProductMembershipRoleType;
}
