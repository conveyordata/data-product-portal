import { DataProductContract } from '@/types/data-product';
import { DataProductDatasetContract } from '@/types/data-product-dataset';

export type DataProductLink = DataProductDatasetContract & {
    data_product: DataProductContract;
};
