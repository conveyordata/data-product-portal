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
    Github = 'github',
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
    | DataPlatforms.Github
    | DataPlatforms.Redshift;
