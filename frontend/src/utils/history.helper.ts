import { TFunction } from 'i18next';

import { EventContract } from '@/types/events/event.contract';
import { EventReferenceEntity } from '@/types/events/event-reference-entity';
import { EventType } from '@/types/events/event-types';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';

export function getTypeDisplayName(t: TFunction, type: EventReferenceEntity): string {
    switch (type) {
        case EventReferenceEntity.Dataset:
            return t('Dataset');
        case EventReferenceEntity.DataProduct:
            return t('Data Product');
        case EventReferenceEntity.DataOutput:
            return t('Data Output');
        case EventReferenceEntity.User:
            return t('User');
    }
}

export function getSubjectDisplayLabel(t: TFunction, record: EventContract): string {
    const { subject_type, deleted_subject_identifier } = record;
    const displayType = ` ${getTypeDisplayName(t, subject_type)}`;

    if (deleted_subject_identifier) {
        return subject_type == EventReferenceEntity.User
            ? deleted_subject_identifier
            : `${deleted_subject_identifier} ${displayType}`;
    }

    switch (subject_type) {
        case EventReferenceEntity.User:
            return record.user.email;
        case EventReferenceEntity.DataProduct:
            return record.data_product.name + displayType;
        case EventReferenceEntity.DataOutput:
            return record.data_output.name + displayType;
        case EventReferenceEntity.Dataset:
            return record.dataset.name + displayType;
    }
}

export function getTargetDisplayLabel(t: TFunction, record: EventContract): string | null {
    const { target_type, deleted_target_identifier, target_id } = record;

    if (!target_id) {
        return null;
    }

    const displayType = ` ${getTypeDisplayName(t, target_type)}`;

    if (deleted_target_identifier) {
        return target_type == EventReferenceEntity.User
            ? deleted_target_identifier
            : `${deleted_target_identifier} ${displayType}`;
    }

    switch (target_type) {
        case EventReferenceEntity.User:
            return record.user.email;
        case EventReferenceEntity.DataProduct:
            return record.data_product.name + displayType;
        case EventReferenceEntity.DataOutput:
            return record.data_output.name + displayType;
        case EventReferenceEntity.Dataset:
            return record.dataset.name + displayType;
    }
}

export function getEventReferenceEntityLinkPath(
    id: string,
    dataProductId: string | null,
    type: EventReferenceEntity,
): string | null {
    switch (type) {
        case EventReferenceEntity.Dataset:
            return createDatasetIdPath(id);
        case EventReferenceEntity.DataProduct:
            return createDataProductIdPath(id);
        case EventReferenceEntity.DataOutput:
            return dataProductId ? createDataOutputIdPath(id, dataProductId) : null;
        case EventReferenceEntity.User:
            return null;
    }
}

export function getEventTypeDisplayName(t: TFunction, type: EventType): string {
    switch (type) {
        case EventType.DATA_OUTPUT_CREATED:
            return t('Data output created');
        case EventType.DATA_OUTPUT_REMOVED:
            return t('Data output removed');
        case EventType.DATA_OUTPUT_STATUS_UPDATED:
            return t('Data output status updated');
        case EventType.DATA_OUTPUT_LINK_REQUESTED_TO_DATASET:
            return t('Data output link requested to dataset');
        case EventType.DATA_OUTPUT_LINK_REMOVED_FROM_DATASET:
            return t('Data output link removed from dataset');
        case EventType.DATA_OUTPUT_UPDATED:
            return t('Data output updated');
        case EventType.DATA_OUTPUT_LINK_TO_DATASET_APPROVED:
            return t('Data output link to dataset approved');
        case EventType.DATA_OUTPUT_LINK_TO_DATASET_DENIED:
            return t('Data output link to dataset denied');
        case EventType.DATA_OUTPUT_LINK_TO_DATASET_REMOVED:
            return t('Data output link to dataset removed');
        case EventType.DATA_PRODUCT_MEMBERSHIP_REQUESTED:
            return t('Data product membership requested');
        case EventType.DATA_PRODUCT_MEMBERSHIP_APPROVED:
            return t('Data product membership approved');
        case EventType.DATA_PRODUCT_MEMBERSHIP_DENIED:
            return t('Data product membership denied');
        case EventType.DATA_PRODUCT_MEMBERSHIP_REMOVED:
            return t('Data product membership removed');
        case EventType.DATA_PRODUCT_MEMBERSHIP_CREATED:
            return t('Data product membership created');
        case EventType.DATA_PRODUCT_MEMBERSHIP_UPDATED:
            return t('Data product membership updated');
        case EventType.DATA_PRODUCT_CREATION_MEMBERSHIP_ADDED:
            return t('Data product creation: membership added');
        case EventType.DATA_PRODUCT_CREATED:
            return t('Data product created');
        case EventType.DATA_PRODUCT_DELETED:
            return t('Data product deleted');
        case EventType.DATA_PRODUCT_UPDATE_MEMBERSHIP_UPDATED:
            return t('Data product update: membership updated');
        case EventType.DATA_PRODUCT_UPDATE_MEMBERSHIP_REMOVED:
            return t('Data product update: membership removed');
        case EventType.DATA_PRODUCT_UPDATE_MEMBERSHIP_ADDED:
            return t('Data product update: membership added');
        case EventType.DATA_PRODUCT_UPDATED:
            return t('Data product updated');
        case EventType.DATA_PRODUCT_ABOUT_UPDATED:
            return t('Data product about updated');
        case EventType.DATA_PRODUCT_STATUS_UPDATED:
            return t('Data product status updated');
        case EventType.DATA_PRODUCT_REQUESTED_ACCESS_TO_DATASET:
            return t('Data product requested access to dataset');
        case EventType.DATA_PRODUCT_LINKED_TO_DATASET:
            return t('Data product linked to dataset');
        case EventType.DATA_PRODUCT_ACCESS_REQUEST_TO_DATASET_REMOVED:
            return t('Data product access request to dataset removed');
        case EventType.DATA_PRODUCT_UNLINKED_FROM_DATASET:
            return t('Data product unlinked from dataset');
        case EventType.DATA_PRODUCT_LINK_TO_DATASET_APPROVED:
            return t('Data product link to dataset approved');
        case EventType.DATA_PRODUCT_LINK_TO_DATASET_DENIED:
            return t('Data product link to dataset denied');
        case EventType.DATA_PRODUCT_LINK_TO_DATASET_REMOVED:
            return t('Data product link to dataset removed');
        case EventType.DATASET_CREATION_OWNER_ADDED:
            return t('Dataset creation: owner added');
        case EventType.DATASET_CREATED:
            return t('Dataset created');
        case EventType.DATASET_REMOVED:
            return t('Dataset removed');
        case EventType.DATASET_UPDATE_OWNER_REMOVED:
            return t('Dataset update: owner removed');
        case EventType.DATASET_UPDATE_OWNER_ADDED:
            return t('Dataset update: owner added');
        case EventType.DATASET_UPDATED:
            return t('Dataset updated');
        case EventType.DATASET_ABOUT_UPDATED:
            return t('Dataset about updated');
        case EventType.DATASET_STATUS_UPDATED:
            return t('Dataset status updated');
        case EventType.USER_ADDED_TO_DATASET:
            return t('User added to dataset');
        case EventType.USER_REMOVED_FROM_DATASET:
            return t('User removed from dataset');
        default:
            return 'Unknown';
    }
}
