import { BusinessAreaContract } from '@/types/business-area';
import { DataProductContract } from '../data-product';
import { DatasetContract } from '../dataset';

export type BusinessAreasGetContract = BusinessAreaContract & {
    data_product_count: number;
    dataset_count: number;
};
export type BusinessAreaGetContract = BusinessAreaContract & {
    data_products: DataProductContract[];
    datasets: DatasetContract[];
};
