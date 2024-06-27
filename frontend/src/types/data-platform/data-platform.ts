export enum DataPlataforms {
    AWS = 'aws',
    Conveyor = 'conveyor',
    ConveyorNotebook = 'conveyor-notebook',
    Tableau = 'tableau',
    Databricks = 'databricks',
    Collibra = 'collibra',
    Datahub = 'datahub',
    Snowflake = 'snowflake',
}

export type DataPlatform =
    | DataPlataforms.AWS
    | DataPlataforms.Conveyor
    | DataPlataforms.ConveyorNotebook
    | DataPlataforms.Databricks
    | DataPlataforms.Collibra
    | DataPlataforms.Datahub
    | DataPlataforms.Tableau
    | DataPlataforms.Snowflake;
