import type { DomainContract } from './domain.contract';

export type DomainsGetContract = DomainContract & {
    data_product_count: number;
};
