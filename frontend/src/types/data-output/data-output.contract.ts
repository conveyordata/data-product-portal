import { DataProductContract } from '@/types/data-product';
import { TagContract } from '@/types/tag';

import { DataOutputConfiguration } from '.';
import { DataOutputDatasetLink } from './dataset-link.contract';

export enum DataOutputConfigurationTypes {
    S3DataOutput = 'S3DataOutput',
    GlueDataOutput = 'GlueDataOutput',
    DatabricksDataOutput = 'DatabricksDataOutput',
    SnowflakeDataOutput = 'SnowflakeDataOutput',
    RedshiftDataOutput = 'RedshiftDataOutput',
}

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
    configuration: DataOutputConfiguration;
    //configuration_type: string;
    platform_id: string;
    service_id: string;
    dataset_links: DataOutputDatasetLink[];
    tag_ids: string[];
    tags: TagContract[];
}

export interface DataOutputModel extends DataOutputContract {}
//export type DataOutput = DataOutputContract
