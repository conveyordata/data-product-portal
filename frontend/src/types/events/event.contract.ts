import { DataOutputContract } from '../data-output';
import { DataProductContract } from '../data-product';
import { DatasetContract } from '../dataset';
import { DomainContract } from '../domain';
import { UserContract } from '../users';

export interface EventContract {
    name: string;
    subject_id: string;
    target_id: string;
    data_product: DataProductContract;
    user: UserContract;
    dataset: DatasetContract;
    data_output: DataOutputContract;
    domain: DomainContract;
    actor: UserContract;
    created_on: string;
}
