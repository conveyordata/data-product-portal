import { TagContract } from '@/types/tag';
import { DatasetContract } from '@/types/dataset';

export type DatasetsGetContract = (Omit<DatasetContract, 'data_product_links' | 'owners' | 'tags'> & {
    data_product_count: number;
    tags: Omit<TagContract, 'id'>[];
    rolled_up_tags: Omit<TagContract, 'id'>[];
})[];
