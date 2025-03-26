import { DatasetMembershipContract } from '@/types/dataset-membership';

export interface DatasetMembershipRequestAccessRequest {
    datasetId: string;
    userId: string;
}

export type DatasetMembershipRequestAccessResponse = DatasetMembershipContract;
