export interface GlueDataOutputContract {
    database: string;
    database_suffix: string | undefined;
    table: string;
    bucket_identifier: string | undefined;
    database_path: string | undefined;
    table_path: string | undefined;
    configuration_type: string;
}

export interface GlueDataOutputModel extends GlueDataOutputContract {}
export type GlueDataOutput = GlueDataOutputContract;
