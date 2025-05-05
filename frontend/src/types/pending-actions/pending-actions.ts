import { DataOutputDatasetLinkRequest } from '../data-output-dataset';
import { DataProductDatasetLinkRequest } from '../data-product-dataset';

export enum PendingActionTypes {
    DataProductDataset = 'DataProductDataset',
    DataProductMembership = 'DataProductMembership',
    DataOutputDataset = 'DataOutpuDataset',
}

export type ActionResolveRequest =
    | { type: PendingActionTypes.DataOutputDataset; request: DataOutputDatasetLinkRequest }
    | { type: PendingActionTypes.DataProductDataset; request: DataProductDatasetLinkRequest }
    | { type: PendingActionTypes.DataProductMembership; request: string };
