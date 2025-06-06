import type { DataOutputDatasetContract } from '@/types/data-output-dataset';

import type { DataOutputContract } from '../data-output';

export type DataOutputLink = Omit<DataOutputDatasetContract, 'dataset'> & {
    data_output: DataOutputContract;
};
