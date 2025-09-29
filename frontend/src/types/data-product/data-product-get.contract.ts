import type { DataProductContract } from '@/types/data-product';
import type { TagContract } from '@/types/tag';
import type { DataProductRoleAssignmentContract } from '../roles/role.contract';

export type DataProductsGetContract = (Omit<
    DataProductContract,
    'users' | 'data_outputs' | 'dataset_links' | 'tags'
> & {
    user_count: number;
    owner_count: number;
    dataset_count: number;
    data_outputs_count: number;
    tags: Omit<TagContract, 'id'>[];
    rolled_up_tags: Omit<TagContract, 'id'>[];
    assignments: DataProductRoleAssignmentContract[];
})[];
