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

        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_CREATED:
            return '';
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_UPDATED:
            return t('role assignment updated for user ');
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REMOVED:
            return t('role assignment removed for user ');
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REQUESTED:
            return '';
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_APPROVED:
            return t('role assignment approved for user ');
        case EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_DENIED:
            return t('role assignment denied for user ');

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

        case EventType.DATASET_ROLE_ASSIGNMENT_CREATED:
            return '';
        case EventType.DATASET_ROLE_ASSIGNMENT_UPDATED:
            return t('role assignment updated for user ');
        case EventType.DATASET_ROLE_ASSIGNMENT_REMOVED:
            return t('role assignment removed for user ');
        case EventType.DATASET_ROLE_ASSIGNMENT_REQUESTED:
            return '';
        case EventType.DATASET_ROLE_ASSIGNMENT_APPROVED:
            return t('role assignment approved for user ');
        case EventType.DATASET_ROLE_ASSIGNMENT_DENIED:
            return t('role assignment denied for user ');

        default:
            return '';
    }
}
