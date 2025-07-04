import type { DataOutputContract } from './data-output.contract';

export type DataOutputCreate = Pick<
    DataOutputContract,
    'name' | 'status' | 'configuration' | 'description' | 'namespace' | 'tag_ids'
> & {
    platform_id: string;
    service_id: string;
    sourceAligned: boolean;
};

export type DataOutputCreateFormSchema = DataOutputCreate & {
    result: string;
};

export type DataOutputCreateResponse = {
    id: string;
};
