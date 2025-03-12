import { DataOutputContract } from '@/types/data-output';
import { DataOutputDatasetLinkStatus } from '@/types/data-output-dataset';
import { UserContract } from '@/types/users';

import { DatasetContract } from '../dataset';

export type DataOutputDatasetContract = {
    id: string;
    data_output_id: string;
    dataset_id: string;
    data_output: DataOutputContract;
    dataset: DatasetContract;
    status: DataOutputDatasetLinkStatus;
    requested_by: UserContract;
    denied_by: UserContract | null;
    approved_by: UserContract | null;
    requested_on: string;
    denied_on: string | null;
    approved_on: string | null;
};
