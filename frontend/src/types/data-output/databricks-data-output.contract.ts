export interface DatabricksDataOutputContract {
    catalog: string;
    schema: string | undefined;
    bucket_identifier: string | undefined;
    catalog_path: string | undefined;
    configuration_type: string;
    table: string | undefined;
    table_path: string | undefined;
}

export interface DatabricksDataOutputModel extends DatabricksDataOutputContract {}
export type DatabricksDataOutput = DatabricksDataOutputContract;
