import { TFunction } from 'i18next';

import { EventContract } from '@/types/events/event.contract';
import { EventObject } from '@/types/events/event-object-type';

export function getTypeDisplayName(t: TFunction, type: EventObject): string {
    switch (type) {
        case EventObject.Dataset:
            return t('Dataset');
        case EventObject.DataProduct:
            return t('Data Product');
        case EventObject.DataOutput:
            return t('Data Output');
        case EventObject.User:
            return t('User');
    }
}

export function getSubjectDisplayLabel(t: TFunction, record: EventContract): string {
    const { subject_type, deleted_subject_identifier } = record;
    const displayType = ' ' + getTypeDisplayName(t, subject_type);

    if (deleted_subject_identifier) {
        return subject_type == EventObject.User
            ? deleted_subject_identifier
            : `${deleted_subject_identifier} ${displayType}`;
    }

    switch (subject_type) {
        case EventObject.User:
            return record.user.email;
        case EventObject.DataProduct:
            return record.data_product.name + displayType;
        case EventObject.DataOutput:
            return record.data_output.name + displayType;
        case EventObject.Dataset:
            return record.dataset.name + displayType;
    }
}

export function getTargetDisplayLabel(t: TFunction, record: EventContract): string | null {
    const { target_type, deleted_target_identifier, target_id } = record;

    if (!target_id) {
        return null;
    }

    const displayType = getTypeDisplayName(t, target_type);

    if (deleted_target_identifier) {
        return target_type == EventObject.User
            ? deleted_target_identifier
            : `${deleted_target_identifier} ${displayType}`;
    }

    switch (target_type) {
        case EventObject.User:
            return record.user.email;
        case EventObject.DataProduct:
            return `${record.data_product.name} ${displayType}`;
        case EventObject.DataOutput:
            return `${record.data_output.name} ${displayType}`;
        case EventObject.Dataset:
            return `${record.dataset.name} ${displayType}`;
    }
}
