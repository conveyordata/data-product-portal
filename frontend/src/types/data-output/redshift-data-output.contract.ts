export interface RedshiftDataOutputContract {
    database: string;
    schema: string | undefined;
    configuration_type: string;
    schema_path: string | undefined;
    table: string | undefined;
    table_path: string | undefined;
}

export interface RedshiftDataOutputModel extends RedshiftDataOutputContract {}
export type RedshiftDataOutput = RedshiftDataOutputContract;
