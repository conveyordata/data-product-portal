import { TFunction } from 'i18next';

import { EventContract } from '@/types/events/event.contract';
import { EventReferenceEntity } from '@/types/events/event-reference-entity';
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
