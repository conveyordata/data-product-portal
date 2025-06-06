import type { DataProductContract } from '@/types/data-product';
import type { DataProductDatasetContract } from '@/types/data-product-dataset';

export type DataProductLink = DataProductDatasetContract & {
    data_product: DataProductContract;
};
