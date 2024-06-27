import { TagContract } from '@/types/tag';
import { DataProductContract } from '@/types/data-product';

export type DataProductsGetContract = (Omit<DataProductContract, 'users' | 'dataset_links' | 'owners' | 'tags'> & {
    user_count: number;
    owner_count: number;
    dataset_count: number;
    tags: Omit<TagContract, 'id'>[];
})[];
