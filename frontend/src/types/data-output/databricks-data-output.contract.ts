export interface DatabricksDataOutputContract {
    schema: string;
    schema_suffix: string | undefined;
    bucket_identifier: string | undefined;
    schema_path: string | undefined;
    configuration_type: string;
}

export interface DatabricksDataOutputModel extends DatabricksDataOutputContract {}
export type DatabricksDataOutput = DatabricksDataOutputContract;
