import { TagContract } from '@/types/tag';
import { DataProductTypeContract } from '@/types/data-product-type';
import { DataProductMembershipContract } from '@/types/data-product-membership';
import { BusinessAreaContract } from '@/types/business-area';
import { DatasetLink } from '@/types/data-product/dataset-link.contract.ts';
import { DataOutputContract } from '@/types/data-output/data-output-contract.ts';

export enum DataProductStatus {
    Pending = 'pending',
    Active = 'active',
    Archived = 'archived',
}

export interface DataProductContract {
    id: string;
    name: string;
    description: string;
    about: string;
    type: DataProductTypeContract;
    type_id: string;
    status: DataProductStatus;
    dataset_links: DatasetLink[];
    tags: TagContract[];
    memberships: DataProductMembershipContract[];
    business_area: BusinessAreaContract;
    business_area_id: string;
    external_id: string;
    data_outputs: DataOutputContract[];
}

export interface DataProductModel extends DataProductContract {}
