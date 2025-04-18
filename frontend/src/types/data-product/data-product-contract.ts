import { DataOutputsGetContract } from '@/types/data-output/data-output-get.contract.ts';
import { DatasetLink } from '@/types/data-product/dataset-link.contract.ts';
import { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import { DataProductMembershipContract } from '@/types/data-product-membership';
import { DataProductTypeContract } from '@/types/data-product-type';
import { DomainContract } from '@/types/domain';
import { TagContract } from '@/types/tag';

import { DataProductSettingValueContract } from '../data-product-setting';

export enum DataProductStatus {
    Pending = 'pending',
    Active = 'active',
    Deleted = 'deleted',
}

export interface DataProductContract {
    id: string;
    name: string;
    description: string;
    about: string;
    type: DataProductTypeContract;
    type_id: string;
    status: DataProductStatus;
    lifecycle: DataProductLifeCycleContract;
    lifecycle_id: string;
    dataset_links: DatasetLink[];
    tag_ids: string[];
    tags: TagContract[];
    rolled_up_tags: TagContract[];
    memberships: DataProductMembershipContract[];
    domain: DomainContract;
    domain_id: string;
    namespace: string;
    data_outputs: DataOutputsGetContract;
    data_product_settings: DataProductSettingValueContract[];
}

export interface DataProductModel extends DataProductContract {}
