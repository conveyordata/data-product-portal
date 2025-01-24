import { TagCreate } from '@/types/tag';
import { DataProductUserMembershipCreateContract } from '@/types/data-product-membership';
import { DataProductContract } from '@/types/data-product/data-product-contract.ts';

export type DataProductCreate = Pick<
    DataProductContract,
    'name' | 'description' | 'type_id' | 'lifecycle_id' | 'business_area_id'
> & {
    external_id: string;
    memberships: DataProductUserMembershipCreateContract[];
    tags: TagCreate[];
};

export type DataProductCreateFormSchema = Omit<DataProductCreate, 'tags'> & {
    owners: string[];
    members: string[];
    tags: string[];
};

export type DataProductCreateResponse = {
    id: string;
};
