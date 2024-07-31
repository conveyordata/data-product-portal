import { S3DataOutputForm } from '@/components/data-products/data-output-form/s3-data-output-form.component.tsx';
import { GlueDataOutput } from './glue-data-output.contract.ts';
import { S3DataOutput, S3DataOutputContract } from './s3-data-output.contract.ts';
import { GlueDataOutputForm } from '@/components/data-products/data-output-form/glue-data-output-form.component.tsx';

export type { DataOutputContract, DataOutput } from './data-output.contract.ts';
export type {
    DataOutputCreate,
    DataOutputCreateFormSchema,
    DataOutputCreateResponse,
} from './data-output-create.contract.ts';
export type { S3DataOutputContract, S3DataOutput } from './s3-data-output.contract.ts';
export type { GlueDataOutputContract, GlueDataOutput } from './glue-data-output.contract.ts';
export type {
    DataOutputDatasetRemoveRequest,
    DataOutputDatasetRemoveResponse,
} from './data-output-dataset-remove.contract.ts';
export type {
    DataOutputDatasetAccessRequest,
    DataOutputDatasetAccessResponse,
} from './data-output-dataset-access.contract.ts';

export interface DataOutputConfigurationContract {
    config: GlueDataOutput | S3DataOutput;
}

export type DataOutputConfiguration = S3DataOutput | GlueDataOutput;
