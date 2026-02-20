import type { DataOutputContract } from './data-output.contract';
import type { TechnicalMappingContract } from './technical-mapping.contract';

export type DataOutputCreate = Pick<
    DataOutputContract,
    'name' | 'status' | 'configuration' | 'description' | 'namespace' | 'tag_ids'
> & {
    platform_id: string;
    service_id: string;
    technical_mapping: TechnicalMappingContract;
};

export type DataOutputCreateFormSchema = DataOutputCreate & {
    result: string;
};
