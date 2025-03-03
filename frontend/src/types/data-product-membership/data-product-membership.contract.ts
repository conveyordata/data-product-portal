import { DataProductMembershipRoleType, DataProductMembershipStatus } from '@/types/data-product-membership';
import { UserContract } from '@/types/users';

import { DataProductContract } from '../data-product';

export interface DataProductMembershipContract {
    id: string;
    data_product_id: string;
    user_id: string;
    role: DataProductMembershipRoleType;
    status: DataProductMembershipStatus;
    user: UserContract;
    data_product: DataProductContract;
}

export interface DataProductMembershipModel extends DataProductMembershipContract {}
