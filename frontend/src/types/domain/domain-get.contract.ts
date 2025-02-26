import { DataProductContract } from '../data-product';
import { DatasetContract } from '../dataset';
import { DomainContract } from './domain.contract';

export type DomainsGetContract = DomainContract & {
    data_product_count: number;
    dataset_count: number;
};
export type DomainGetContract = DomainContract & {
    data_products: DataProductContract[];
    datasets: DatasetContract[];
};
