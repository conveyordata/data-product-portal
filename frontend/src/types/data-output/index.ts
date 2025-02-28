import { DatabricksDataOutput } from './databricks-data-output.contract.ts';
import { GlueDataOutput } from './glue-data-output.contract.ts';
import { RedshiftDataOutput } from './redshift-data-output.contract.ts';
import { S3DataOutput } from './s3-data-output.contract.ts';
import { SnowflakeDataOutput } from './snowflake-data-output.contract.ts';

export type { DataOutputsGetContract } from './data-outputs-get.contract.ts';
export { DataOutputStatus } from './data-output.contract.ts';
export type { DataOutputDatasetLink } from './dataset-link.contract.ts';
export type { DataOutputContract } from './data-output.contract.ts';
export type {
    DataOutputCreate,
    DataOutputCreateFormSchema,
    DataOutputCreateResponse,
} from './data-output-create.contract.ts';
export type { S3DataOutputContract, S3DataOutput } from './s3-data-output.contract.ts';
export type { RedshiftDataOutputContract, RedshiftDataOutput } from './redshift-data-output.contract.ts';
export type { GlueDataOutputContract, GlueDataOutput } from './glue-data-output.contract.ts';
export type { DatabricksDataOutputContract, DatabricksDataOutput } from './databricks-data-output.contract.ts';
export type { SnowflakeDataOutputContract, SnowflakeDataOutput } from './snowflake-data-output.contract.ts';
export type {
    DataOutputDatasetRemoveRequest,
    DataOutputDatasetRemoveResponse,
} from './data-output-dataset-remove.contract.ts';
export type {
    DataOutputDatasetAccessRequest,
    DataOutputDatasetAccessResponse,
} from './data-output-dataset-access.contract.ts';

export interface DataOutputConfigurationContract {
    config: GlueDataOutput | S3DataOutput | DatabricksDataOutput | SnowflakeDataOutput | RedshiftDataOutput;
}

export type DataOutputConfiguration =
    | S3DataOutput
    | GlueDataOutput
    | DatabricksDataOutput
    | SnowflakeDataOutput
    | RedshiftDataOutput;
