import type { DataOutputsGetContract } from '@/types/data-output/data-output-get.contract.ts';
import type { DatasetLink } from '@/types/data-product/dataset-link.contract.ts';
import type { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import type { DataProductTypeContract } from '@/types/data-product-type';
import type { DomainContract } from '@/types/domain';
import type { TagContract } from '@/types/tag';

import type { DataProductSettingValueContract } from '../data-product-setting';

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
    domain: DomainContract;
    domain_id: string;
    namespace: string;
    usage?: string;
    data_outputs: DataOutputsGetContract;
    data_product_settings: DataProductSettingValueContract[];
}

export interface DataProductModel extends DataProductContract {}
