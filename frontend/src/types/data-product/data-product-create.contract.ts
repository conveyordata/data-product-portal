import { DataProductContract } from '@/types/data-product/data-product-contract.ts';
import { DataProductUserMembershipCreateContract } from '@/types/data-product-membership';

export type DataProductCreate = Pick<
    DataProductContract,
    'name' | 'description' | 'type_id' | 'lifecycle_id' | 'domain_id' | 'tag_ids'
> & {
    external_id: string;
    memberships: DataProductUserMembershipCreateContract[];
};

export type DataProductCreateFormSchema = DataProductCreate & {
    owners: string[];
    members: string[];
};

export type DataProductCreateResponse = {
    id: string;
};
