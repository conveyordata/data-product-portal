import type { DataProductContract } from '@/types/data-product/data-product-contract.ts';

export type DataProductCreate = Pick<
    DataProductContract,
    'name' | 'description' | 'type_id' | 'lifecycle_id' | 'domain_id' | 'tag_ids'
> & {
    namespace: string;
    owners: string[];
};

export type DataProductCreateFormSchema = DataProductCreate;

export type DataProductCreateResponse = {
    id: string;
};
