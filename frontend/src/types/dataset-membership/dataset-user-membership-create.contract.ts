import { DatasetMembershipContract } from '@/types/dataset-membership';

export type DatasetUserMembershipCreateContract = Pick<DatasetMembershipContract, 'user_id' | 'role'>;
