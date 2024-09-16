import { DataOutputConfiguration } from '.';
import { DataProductContract } from '../data-product/data-product-contract';
import { DataOutputDatasetLink } from './dataset-link.contract';

export enum DataOutputConfigurationTypes {
    S3DataOutput = 'S3DataOutput',
    GlueDataOutput = 'GlueDataOutput',
}

export enum DataOutputStatus {
    Pending = 'pending',
    Active = 'active',
    Archived = 'archived',
}

export interface DataOutputContract {
    id: string;
    external_id: string;
    description: string;
    name: string;
    status: DataOutputStatus;
    owner: DataProductContract;
    owner_id: string;
    configuration: DataOutputConfiguration;
    configuration_type: string;
    platform_id: string;
    service_id: string;
    dataset_links: DataOutputDatasetLink[];
}

export interface DataOutputModel extends DataOutputContract {}
//export type DataOutput = DataOutputContract
