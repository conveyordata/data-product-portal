export type DataProductIcon =
    | 'reporting'
    | 'processing'
    | 'exploration'
    | 'ingestion'
    | 'machine_learning'
    | 'analytics'
    | 'default';

export interface DataProductTypeContract {
    id: string;
    name: string;
    description: string;
    icon_key: DataProductIcon;
}

export interface DataProductTypeModel extends DataProductTypeContract {}
