import { DatasetMembershipRoleType, DatasetMembershipStatus } from '@/types/dataset-membership';
import { UserContract } from '@/types/users';

import { DatasetContract } from '../dataset';

export interface DatasetMembershipContract {
    id: string;
    dataset_id: string;
    user_id: string;
    role: DatasetMembershipRoleType;
    status: DatasetMembershipStatus;
    user: UserContract;
    dataset: DatasetContract;
    requested_on: string;
    approved_by?: UserContract | null;
    approved_on?: string | null;
    denied_by?: UserContract | null;
    denied_on?: string | null;
}

export interface DatasetMembershipModel extends DatasetMembershipContract {}
