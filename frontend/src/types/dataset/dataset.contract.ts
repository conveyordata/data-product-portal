import { TagContract } from '@/types/tag';
import { UserContract } from '@/types/users';
import { DataProductLink } from '@/types/dataset';
import { BusinessAreaContract } from '@/types/business-area';

export enum DatasetStatus {
    Pending = 'pending',
    Active = 'active',
    Archived = 'archived',
}

export enum DatasetAccess {
    Public = 'public',
    Restricted = 'restricted',
}
export const datasetStatusList = [DatasetStatus.Pending, DatasetStatus.Active, DatasetStatus.Archived];

export interface DatasetContract {
    id: string;
    name: string;
    description: string;
    about: string;
    owners: UserContract[];
    status: DatasetStatus;
    tags: TagContract[];
    data_product_links: DataProductLink[];
    access_type: DatasetAccess;
    business_area: BusinessAreaContract;
    external_id: string;
}

export interface DatasetModel extends DatasetContract {}
