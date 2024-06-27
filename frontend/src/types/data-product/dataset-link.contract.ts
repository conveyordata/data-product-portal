import { DatasetContract } from '@/types/dataset';
import { DataProductDatasetContract } from '../data-product-dataset';

export type DatasetLink = DataProductDatasetContract & {
    dataset: DatasetContract;
};
