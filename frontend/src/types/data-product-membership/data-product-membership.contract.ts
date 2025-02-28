import { UserContract } from '@/types/users';
import { DataProductMembershipRoleType, DataProductMembershipStatus } from '@/types/data-product-membership';
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

interface DataProductMembership {
    user_id: string;
    role: DataProductMembershipRoleType;
    id: string;
    data_product_id: string;
    status: DataProductMembershipStatus;
    requested_on: string;
    requested_by: UserContract;
    approved_by?: UserContract | null;
    approved_on?: string | null;
    denied_by?: UserContract | null;
    denied_on?: string | null;
}

export interface DataProductMembershipAssociation {
    id: string;
    data_product_id: string;
    user_id: string;
    membership_id: string;
    role: DataProductMembershipRoleType;
    status: DataProductMembershipStatus;
    membership: DataProductMembership;
    user: UserContract;
    data_product: DataProductContract;
}
