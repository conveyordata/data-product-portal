import type { DatasetContract } from '@/types/dataset';

import type { DataProductDatasetContract } from '../data-product-dataset';

export type DatasetLink = DataProductDatasetContract & {
    dataset: DatasetContract;
};
