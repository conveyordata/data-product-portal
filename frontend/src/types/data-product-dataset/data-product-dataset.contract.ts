import type { UserContract } from '@/types/users';

import type { DataProductContract } from '../data-product';
import type { DatasetContract } from '../dataset';
import type { DecisionStatus } from '../roles';

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
