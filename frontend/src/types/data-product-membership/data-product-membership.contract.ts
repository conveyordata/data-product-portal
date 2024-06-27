import { UserContract } from '@/types/users';
import { DataProductMembershipRoleType, DataProductMembershipStatus } from '@/types/data-product-membership';

export interface DataProductMembershipContract {
    id: string;
    data_product_id: string;
    user_id: string;
    role: DataProductMembershipRoleType;
    status: DataProductMembershipStatus;
    user: UserContract;
}

export interface DataProductMembershipModel extends DataProductMembershipContract {}
