export enum DataProductIcon {
    Reporting = 'reporting',
    Processing = 'processing',
    Exploration = 'exploration',
    Ingestion = 'ingestion',
    MachineLearning = 'machine_learning',
    Analytics = 'analytics',
    Default = 'default',
}

export const dataProductIcons = Object.values(DataProductIcon);

export interface DataProductTypeContract {
    id: string;
    name: string;
    description: string;
    icon_key: DataProductIcon;
}

export interface DataProductTypeModel extends DataProductTypeContract {}
