export enum DataPlatforms {
    AWS = 'aws',
    Conveyor = 'conveyor',
    ConveyorNotebook = 'conveyor-notebook',
    Tableau = 'tableau',
    Databricks = 'databricks',
    Collibra = 'collibra',
    Datahub = 'datahub',
    Snowflake = 'snowflake',
    S3 = 's3',
    Glue = 'glue',
}

export type DataPlatform =
    | DataPlatforms.AWS
    | DataPlatforms.Conveyor
    | DataPlatforms.ConveyorNotebook
    | DataPlatforms.Databricks
    | DataPlatforms.Collibra
    | DataPlatforms.Datahub
    | DataPlatforms.Tableau
    | DataPlatforms.Snowflake
    | DataPlatforms.S3
    | DataPlatforms.Glue;
