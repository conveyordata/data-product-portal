import { UserContract } from '@/types/users';
import { DataProductDatasetLinkStatus } from '@/types/data-product-dataset';

export type DataProductDatasetContract = {
    id: string;
    data_product_id: string;
    dataset_id: string;
    status: DataProductDatasetLinkStatus;
    requested_by: UserContract;
    denied_by: UserContract | null;
    approved_by: UserContract | null;
    requested_on: string;
    denied_on: string | null;
    approved_on: string | null;
};
