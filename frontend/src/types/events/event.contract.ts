import { DataProductContract } from '../data-product';
import { DatasetContract } from '../dataset';
import { UserContract } from '../users';

export interface EventContract {
    name: string;
    subject_id: string;
    target_id: string;
    data_product: DataProductContract;
    user: UserContract;
    dataset: DatasetContract;
    actor: UserContract;
    created_on: string;
}
