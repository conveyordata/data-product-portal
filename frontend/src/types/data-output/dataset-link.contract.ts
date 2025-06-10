import type { DataOutputDatasetContract } from '../data-output-dataset';
import type { DatasetContract } from '../dataset';

export type DataOutputDatasetLink = DataOutputDatasetContract & {
    dataset: DatasetContract;
};
