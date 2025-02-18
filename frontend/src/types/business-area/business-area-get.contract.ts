import { BusinessAreaContract } from '@/types/business-area';
import { DataProductContract } from '../data-product';
import { DatasetContract } from '../dataset';

export type BusinessAreasGetResponse = BusinessAreaContract;
export type BusinessAreaGetResponse = BusinessAreaContract & {
    data_products: DataProductContract[];
    datasets: DatasetContract[];
};
