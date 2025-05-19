import { DataOutputContract } from '../data-output';
import { DataProductContract } from '../data-product';
import { DatasetContract } from '../dataset';
import { UserContract } from '../users';
import { EventReferenceEntity } from './event-reference-entity';

export interface EventContract {
    name: string;
    deleted_subject_identifier: string;
    deleted_target_identifier: string;
    subject_type: EventReferenceEntity;
    target_type: EventReferenceEntity;
    subject_id: string;
    target_id: string;
    data_product: DataProductContract;
    user: UserContract;
    dataset: DatasetContract;
    data_output: DataOutputContract;
    actor: UserContract;
    created_on: string;
}
