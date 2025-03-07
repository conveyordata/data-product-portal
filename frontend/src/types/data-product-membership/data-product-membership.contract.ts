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
    requested_on: string;
    approved_by?: UserContract | null;
    approved_on?: string | null;
    denied_by?: UserContract | null;
    denied_on?: string | null;
}

export interface DataProductMembershipModel extends DataProductMembershipContract {}
