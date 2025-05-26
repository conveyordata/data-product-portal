import { TFunction } from 'i18next';

import { EventType } from '@/types/events/event-types';

export function getEventTypeNotificationText(t: TFunction, type: EventType): string {
    switch (type) {
        case EventType.DATA_OUTPUT_CREATED:
            return 'has been created for the ';
        case EventType.DATA_OUTPUT_UPDATED:
            return '';
        case EventType.DATA_OUTPUT_REMOVED:
            return 'has been removed from the ';

        case EventType.DATA_OUTPUT_DATASET_LINK_REQUESTED:
            return '';
        case EventType.DATA_OUTPUT_DATASET_LINK_APPROVED:
            return t('is now linked to the ');
        case EventType.DATA_OUTPUT_DATASET_LINK_DENIED:
            return t('link denied for the ');
        case EventType.DATA_OUTPUT_DATASET_LINK_REMOVED:
            return t('has been unlinked from the ');

        case EventType.DATA_PRODUCT_CREATED:
            return 'has been created';
        case EventType.DATA_PRODUCT_UPDATED:
            return '';
        case EventType.DATA_PRODUCT_REMOVED:
            return 'has been removed';

        case EventType.DATA_PRODUCT_MEMBERSHIP_CREATED:
            return '';
        case EventType.DATA_PRODUCT_MEMBERSHIP_UPDATED:
            return t('membership updated for user ');
        case EventType.DATA_PRODUCT_MEMBERSHIP_REMOVED:
            return t('membership removed for user ');
        case EventType.DATA_PRODUCT_MEMBERSHIP_REQUESTED:
            return '';
        case EventType.DATA_PRODUCT_MEMBERSHIP_APPROVED:
            return t('membership approved for user ');
        case EventType.DATA_PRODUCT_MEMBERSHIP_DENIED:
            return t('membership denied for user ');

        case EventType.DATA_PRODUCT_DATASET_LINK_REQUESTED:
            return '';
        case EventType.DATA_PRODUCT_DATASET_LINK_APPROVED:
            return t('is now linked to the ');
        case EventType.DATA_PRODUCT_DATASET_LINK_DENIED:
            return t('link denied for the ');
        case EventType.DATA_PRODUCT_DATASET_LINK_REMOVED:
            return t('has removed a link to the ');

        case EventType.DATASET_CREATED:
            return ' has been created';
        case EventType.DATASET_UPDATED:
            return '';
        case EventType.DATASET_REMOVED:
            return ' has been removed';
        case EventType.DATASET_USER_ADDED:
            return 'membership granted to ';
        case EventType.DATASET_USER_REMOVED:
            return 'membership revoked for ';

        default:
            return '';
    }
}
