import type { DataOutputContract } from '../data-output';
import type { DataProductContract } from '../data-product';
import type { DatasetContract } from '../dataset';
import type { UserContract } from '../users';
import type { EventReferenceEntity } from './event-reference-entity';
import type { EventType } from './event-types';

export interface EventContract {
    name: EventType;
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
