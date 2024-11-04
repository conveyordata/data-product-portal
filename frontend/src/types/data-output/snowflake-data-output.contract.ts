export interface SnowflakeDataOutputContract {
    schema: string;
    schema_suffix: string | undefined;
    configuration_type: string;
}

export interface SnowflakeDataOutputModel extends SnowflakeDataOutputContract {}
export type SnowflakeDataOutput = SnowflakeDataOutputContract;
