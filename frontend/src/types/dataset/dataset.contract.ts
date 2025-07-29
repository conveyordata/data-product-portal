import type { DataOutputLink, DataProductLink } from '@/types/dataset';
import type { DomainContract } from '@/types/domain';
import type { TagContract } from '@/types/tag';

import type { DataProductLifeCycleContract } from '../data-product-lifecycle';
import type { DataProductSettingValueContract } from '../data-product-setting';

export enum DatasetStatus {
    Pending = 'pending',
    Active = 'active',
    Deleted = 'deleted',
}

export enum DatasetAccess {
    Public = 'public',
    Restricted = 'restricted',
    Private = 'private',
}

export interface DatasetContract {
    id: string;
    name: string;
    description: string;
    usage?: string;
    about: string;
    status: DatasetStatus;
    tags: TagContract[];
    rolled_up_tags: TagContract[];
    tag_ids: string[];
    data_product_links: DataProductLink[];
    lifecycle: DataProductLifeCycleContract;
    lifecycle_id: string;
    data_output_links: DataOutputLink[];
    access_type: DatasetAccess;
    domain: DomainContract;
    namespace: string;
    data_product_settings: DataProductSettingValueContract[];
}

export interface DatasetModel extends DatasetContract {}
