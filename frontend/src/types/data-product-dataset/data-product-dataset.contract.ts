import { UserContract } from '@/types/users';

import { DataProductContract } from '../data-product';
import { DatasetContract } from '../dataset';
import { DecisionStatus } from '../roles';

export type DataProductDatasetContract = {
    id: string;
    data_product_id: string;
    dataset_id: string;
    dataset: DatasetContract;
    data_product: DataProductContract;
    status: DecisionStatus;
    requested_by: UserContract;
    denied_by: UserContract | null;
    approved_by: UserContract | null;
    requested_on: string;
    denied_on: string | null;
    approved_on: string | null;
};
