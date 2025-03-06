import { DataOutputLink, DataProductLink } from '@/types/dataset';
import { DomainContract } from '@/types/domain';
import { TagContract } from '@/types/tag';
import { UserContract } from '@/types/users';

import { DataProductLifeCycleContract } from '../data-product-lifecycle';
import { DataProductSettingValueContract } from '../data-product-setting';

export enum DatasetStatus {
    Pending = 'pending',
    Active = 'active',
    Deleted = 'deleted',
}

export enum DatasetAccess {
    Public = 'public',
    Restricted = 'restricted',
}
export const datasetStatusList = [DatasetStatus.Pending, DatasetStatus.Active, DatasetStatus.Deleted];

export interface DatasetContract {
    id: string;
    name: string;
    description: string;
    about: string;
    owners: UserContract[];
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
    external_id: string;
    data_product_settings: DataProductSettingValueContract[];
}

export interface DatasetModel extends DatasetContract {}
