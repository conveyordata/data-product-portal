import { DataOutputContract } from '../data-output';
import { DataProductContract } from '../data-product';
import { DatasetContract } from '../dataset';
import { DomainContract } from '../domain';
import { UserContract } from '../users';
import { EventObject } from './event-object-type';

export interface EventContract {
    name: string;
    deleted_subject_identifier: string;
    deleted_target_identifier: string;
    subject_type: EventObject;
    target_type: EventObject;
    subject_id: EventObject;
    target_id: string;
    data_product: DataProductContract;
    user: UserContract;
    dataset: DatasetContract;
    data_output: DataOutputContract;
    domain: DomainContract;
    actor: UserContract;
    created_on: string;
}
