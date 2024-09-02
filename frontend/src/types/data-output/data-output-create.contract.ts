import { DataOutputContract } from './data-output.contract';

export type DataOutputCreate = Pick<DataOutputContract, 'name' | 'status' | 'configuration' | 'description' | 'external_id'> & {
    owner_id: string;
    platform_id: string;
    service_id: string;
    sourceAligned: boolean;
};

export type DataOutputCreateFormSchema = DataOutputCreate & {
    owner: string;
    is_source_aligned: boolean;
};

export type DataOutputCreateResponse = {
    id: string;
};
