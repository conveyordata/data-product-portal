import { DataOutputContract } from '@/types/data-output';
import { UserContract } from '@/types/users';

import { DatasetContract } from '../dataset';
import { DecisionStatus } from '../roles';

export type DataOutputDatasetContract = {
    id: string;
    data_output_id: string;
    dataset_id: string;
    data_output: DataOutputContract;
    dataset: DatasetContract;
    status: DecisionStatus;
    requested_by: UserContract;
    denied_by: UserContract | null;
    approved_by: UserContract | null;
    requested_on: string;
    denied_on: string | null;
    approved_on: string | null;
};
