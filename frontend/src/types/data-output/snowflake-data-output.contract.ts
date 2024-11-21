export interface SnowflakeDataOutputContract {
    schema: string;
    schema_suffix: string | undefined;
    configuration_type: string;
    schema_path: string | undefined;
    table: string | undefined;
    table_path: string | undefined;
}

export interface SnowflakeDataOutputModel extends SnowflakeDataOutputContract {}
export type SnowflakeDataOutput = SnowflakeDataOutputContract;
