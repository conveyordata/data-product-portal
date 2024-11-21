export interface DatabricksDataOutputContract {
    schema: string;
    schema_suffix: string | undefined;
    bucket_identifier: string | undefined;
    schema_path: string | undefined;
    configuration_type: string;
    table: string | undefined;
    table_path: string | undefined;
}

export interface DatabricksDataOutputModel extends DatabricksDataOutputContract {}
export type DatabricksDataOutput = DatabricksDataOutputContract;
