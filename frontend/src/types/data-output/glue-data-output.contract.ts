export interface GlueDataOutputContract {
    glue_schema: string;
    table_prefixes: string[];
}

export interface GlueDataOutputModel extends GlueDataOutputContract {}
export type GlueDataOutput = GlueDataOutputContract
