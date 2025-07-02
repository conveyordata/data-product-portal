import type { DataProductContract } from '@/types/data-product';
import type { TagContract } from '@/types/tag';

import type { TechnicalInfoContract } from './data-output-technical-info.contract';
import type { DataOutputDatasetLink } from './dataset-link.contract';

export enum DataOutputStatus {
    Pending = 'pending',
    Active = 'active',
    Deleted = 'deleted',
}

export interface DataOutputContract {
    id: string;
    namespace: string;
    description: string;
    name: string;
    status: DataOutputStatus;
    owner: DataProductContract;
    owner_id: string;
    configuration: {
        configuration_type: string;
    };
    platform_id: string;
    service_id: string;
    dataset_links: DataOutputDatasetLink[];
    tag_ids: string[];
    tags: TagContract[];
    result_string: string;
    technical_info: TechnicalInfoContract[];
}

export interface DataOutputModel extends DataOutputContract {}
