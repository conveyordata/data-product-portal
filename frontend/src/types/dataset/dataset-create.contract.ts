import type { DatasetContract } from '@/types/dataset';

export type DatasetCreateRequest = Pick<
    DatasetContract,
    'lifecycle_id' | 'description' | 'name' | 'access_type' | 'namespace' | 'tag_ids' | 'data_product_id'
> & {
    owners: string[];
};

export type DatasetCreateResponse = {
    id: string;
};

export type DatasetCreateFormSchema = DatasetCreateRequest;
