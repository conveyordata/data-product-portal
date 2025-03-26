import { UserContract } from '@/types/users';

export interface DatasetMembershipMemberCreateRequest {
    datasetId: string;
    user: UserContract;
}
