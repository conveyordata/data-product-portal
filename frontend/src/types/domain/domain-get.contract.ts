import type { DataProductContract } from '../data-product';
import type { DatasetContract } from '../dataset';
import type { DomainContract } from './domain.contract';

export type DomainsGetContract = DomainContract & {
    data_product_count: number;
    dataset_count: number;
};
export type DomainGetContract = DomainContract & {
    data_products: DataProductContract[];
    datasets: DatasetContract[];
};
