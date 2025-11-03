export interface DataProductDatasetsAccessRequest {
    dataProductId: string;
    datasetIds: string[];
    justification: string;
}

export type DataProductDatasetsAccessResponse = object;
