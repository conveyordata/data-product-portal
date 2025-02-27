import { DatasetContract } from '@/types/dataset';

export type DatasetCreateRequest = Pick<
    DatasetContract,
    'lifecycle_id' | 'description' | 'name' | 'access_type' | 'external_id' | 'tag_ids'
> & {
    owners: string[];
    domain_id: string;
};

export type DatasetCreateResponse = {
    id: string;
};

export type DatasetCreateFormSchema = DatasetCreateRequest;
