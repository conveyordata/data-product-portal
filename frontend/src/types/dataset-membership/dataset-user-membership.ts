import { DatasetMembershipContract } from '@/types/dataset-membership/dataset-membership.contract.ts';

export type DatasetUserMembership = Pick<DatasetMembershipContract, 'user' | 'role' | 'id' | 'status'>;
