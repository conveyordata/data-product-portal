import { DataOutputDatasetContract } from '@/types/data-output-dataset';

import { DataOutputContract } from '../data-output';

export type DataOutputLink = DataOutputDatasetContract & {
    data_output: DataOutputContract;
};
