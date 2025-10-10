import type { DatasetContract } from '@/types/dataset';
import type { TagContract } from '@/types/tag';
import type { DataProductContract } from '../data-product';

export type DatasetsGetContract = (Omit<DatasetContract, 'data_product_links' | 'owners' | 'tags'> & {
    data_product_count: number;
    tags: Omit<TagContract, 'id'>[];
    data_product: DataProductContract;
    rolled_up_tags: Omit<TagContract, 'id'>[];
})[];
