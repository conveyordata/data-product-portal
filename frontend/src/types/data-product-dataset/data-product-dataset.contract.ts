import { DataProductDatasetLinkStatus } from '@/types/data-product-dataset';
import { UserContract } from '@/types/users';

import { DataProductContract } from '../data-product';
import { DatasetContract } from '../dataset';

export type DataProductDatasetContract = {
    id: string;
    data_product_id: string;
    dataset_id: string;
    dataset: DatasetContract;
    data_product: DataProductContract;
    status: DataProductDatasetLinkStatus;
    requested_by: UserContract;
    denied_by: UserContract | null;
    approved_by: UserContract | null;
    requested_on: string;
    denied_on: string | null;
    approved_on: string | null;
};
