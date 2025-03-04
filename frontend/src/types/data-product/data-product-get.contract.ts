import { DataProductContract } from '@/types/data-product';
import { TagContract } from '@/types/tag';

export type DataProductsGetContract = (Omit<
    DataProductContract,
    'users' | 'data_outputs' | 'dataset_links' | 'owners' | 'tags'
> & {
    user_count: number;
    owner_count: number;
    dataset_count: number;
    data_outputs_count: number;
    tags: Omit<TagContract, 'id'>[];
    rolled_up_tags: Omit<TagContract, 'id'>[];
})[];
