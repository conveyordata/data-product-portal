import { DataOutputConfigurationTypes } from '../data-output/data-output.contract';

export enum DataPlatforms {
    AWS = 'aws',
    Conveyor = 'conveyor',
    Tableau = 'tableau',
    Databricks = 'databricks',
    Collibra = 'collibra',
    Datahub = 'datahub',
    Snowflake = 'snowflake',
    S3 = 's3',
    Glue = 'glue',
    Redshift = 'redshift',
    Soda = 'soda',
}

export type DataPlatform =
    | DataPlatforms.AWS
    | DataPlatforms.Conveyor
    | DataPlatforms.Databricks
    | DataPlatforms.Collibra
    | DataPlatforms.Datahub
    | DataPlatforms.Tableau
    | DataPlatforms.Snowflake
    | DataPlatforms.S3
    | DataPlatforms.Glue
    | DataPlatforms.Redshift
    | DataPlatforms.Soda;

export const DataPlatformDataOutputConfigurationMap: Map<DataPlatform, DataOutputConfigurationTypes> = new Map([
    [DataPlatforms.S3, DataOutputConfigurationTypes.S3DataOutput],
    [DataPlatforms.Glue, DataOutputConfigurationTypes.GlueDataOutput],
    [DataPlatforms.Redshift, DataOutputConfigurationTypes.RedshiftDataOutput],
    [DataPlatforms.Databricks, DataOutputConfigurationTypes.DatabricksDataOutput],
    [DataPlatforms.Snowflake, DataOutputConfigurationTypes.SnowflakeDataOutput],
]);
