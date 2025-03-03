import { DatasetContract } from '@/types/dataset';
import { TagContract } from '@/types/tag';

export type DatasetsGetContract = (Omit<DatasetContract, 'data_product_links' | 'owners' | 'tags'> & {
    data_product_count: number;
    tags: Omit<TagContract, 'id'>[];
    rolled_up_tags: Omit<TagContract, 'id'>[];
})[];
