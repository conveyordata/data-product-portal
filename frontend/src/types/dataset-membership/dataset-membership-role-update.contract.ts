import { DatasetMembershipRoleType } from '@/types/dataset-membership';

export interface DatasetMembershipRoleUpdateRequest {
    datasetId: string;
    membershipId: string;
    role: DatasetMembershipRoleType;
}
