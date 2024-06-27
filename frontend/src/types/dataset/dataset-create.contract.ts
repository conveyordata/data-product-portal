import { DatasetContract } from '@/types/dataset';
import { TagCreate } from '@/types/tag';

export type DatasetCreateRequest = Pick<DatasetContract, 'description' | 'name' | 'access_type' | 'external_id'> & {
    owners: string[];
    tags: TagCreate[];
    business_area_id: string;
};

export type DatasetCreateResponse = {
    id: string;
};

export type DatasetCreateFormSchema = Omit<DatasetCreateRequest, 'tags'> & {
    tags: string[];
};
