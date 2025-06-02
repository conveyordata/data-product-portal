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
            return t('Data output created: now linked with the');
        case EventType.DATA_OUTPUT_UPDATED:
            return t('Data output updated');
        case EventType.DATA_OUTPUT_REMOVED:
            return t('Data output removed: link removed with the');

        case EventType.DATA_OUTPUT_DATASET_LINK_REQUESTED:
            return t('Requested data output dataset link to the');
        case EventType.DATA_OUTPUT_DATASET_LINK_APPROVED:
            return t('Approved data output dataset link to the');
        case EventType.DATA_OUTPUT_DATASET_LINK_DENIED:
            return t('Denied data output dataset link to the');
        case EventType.DATA_OUTPUT_DATASET_LINK_REMOVED:
            return t('Removed data output dataset link to the');

        case EventType.DATA_PRODUCT_CREATED:
            return t('Data product created');
        case EventType.DATA_PRODUCT_UPDATED:
            return t('Data product updated');
        case EventType.DATA_PRODUCT_REMOVED:
            return t('Data product removed');

        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_CREATED:
            return t('Created data product role assignment for');
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_UPDATED:
            return t('Updated data product role assignment for');
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REMOVED:
            return t('Removed data product role assignment for');
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REQUESTED:
            return t('Requested data product role assignment for');
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_APPROVED:
            return t('Approved data product role assignment for');
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_DENIED:
            return t('Denied data product role assignment for');

        case EventType.DATA_PRODUCT_DATASET_LINK_REQUESTED:
            return t('Requested data product dataset link to the');
        case EventType.DATA_PRODUCT_DATASET_LINK_APPROVED:
            return t('Approved data product dataset link to the');
        case EventType.DATA_PRODUCT_DATASET_LINK_DENIED:
            return t('Denied data product dataset link to the');
        case EventType.DATA_PRODUCT_DATASET_LINK_REMOVED:
            return t('Removed product dataset link to the');

        case EventType.DATASET_ROLE_ASSIGNMENT_CREATED:
            return t('Created dataset role assignment for');
        case EventType.DATASET_ROLE_ASSIGNMENT_UPDATED:
            return t('Updated dataset role assignment for');
        case EventType.DATASET_ROLE_ASSIGNMENT_REMOVED:
            return t('Removed dataset role assignment for');
        case EventType.DATASET_ROLE_ASSIGNMENT_REQUESTED:
            return t('Requested dataset role assignment for');
        case EventType.DATASET_ROLE_ASSIGNMENT_APPROVED:
            return t('Approved dataset role assignment for');
        case EventType.DATASET_ROLE_ASSIGNMENT_DENIED:
            return t('Denied dataset role assignment for');

        case EventType.DATASET_CREATED:
            return t('Dataset created');
        case EventType.DATASET_UPDATED:
            return t('Dataset updated');
        case EventType.DATASET_REMOVED:
            return t('Dataset removed');

        default:
            return t('Unknown');
    }
}
