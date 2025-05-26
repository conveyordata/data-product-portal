import { TFunction } from 'i18next';

import { EventType } from '@/types/events/event-types';

export function getEventTypeNotificationText(t: TFunction, type: EventType): string {
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

        case EventType.DATA_PRODUCT_MEMBERSHIP_CREATED:
            return t('Created data product membership for');
        case EventType.DATA_PRODUCT_MEMBERSHIP_UPDATED:
            return t('Updated data product membership for');
        case EventType.DATA_PRODUCT_MEMBERSHIP_REMOVED:
            return t('Removed data product membership for');
        case EventType.DATA_PRODUCT_MEMBERSHIP_REQUESTED:
            return t('Requested data product membership for');
        case EventType.DATA_PRODUCT_MEMBERSHIP_APPROVED:
            return t('Approved data product membership for');
        case EventType.DATA_PRODUCT_MEMBERSHIP_DENIED:
            return t('Denied data product membership for');

        case EventType.DATA_PRODUCT_DATASET_LINK_REQUESTED:
            return t('Requested data product dataset link to the');
        case EventType.DATA_PRODUCT_DATASET_LINK_APPROVED:
            return t('is now linked to the ');
        case EventType.DATA_PRODUCT_DATASET_LINK_DENIED:
            return t('link denied for the ');
        case EventType.DATA_PRODUCT_DATASET_LINK_REMOVED:
            return t('has removed a link to the ');

        case EventType.DATASET_CREATED:
            return t('Dataset created');
        case EventType.DATASET_UPDATED:
            return t('Dataset updated');
        case EventType.DATASET_REMOVED:
            return t('Dataset removed');

        case EventType.DATASET_USER_ADDED:
            return t('Added user to the dataset:');
        case EventType.DATASET_USER_REMOVED:
            return t('Removed user from the dataset:');

        default:
            return t('Unknown');
    }
}
