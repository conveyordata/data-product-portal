export interface GlueDataOutputContract {
    glue_database: string;
    table_prefixes: string[];
    configuration_type: string;
}

export interface GlueDataOutputModel extends GlueDataOutputContract {}
export type GlueDataOutput = GlueDataOutputContract;
