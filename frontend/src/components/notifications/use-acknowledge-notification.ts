import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
    type GetUserNotificationsResponseItem,
    useRemoveUserNotificationMutation,
} from '@/store/api/services/generated/usersNotificationsApi.ts';
import { EventType } from '@/types/events/event-types.ts';
import { dispatchMessage } from '@/utils/feedback.ts';

export function isAnnouncementNotification(notification: GetUserNotificationsResponseItem) {
    return notification.event.name === EventType.ANNOUNCEMENT_CREATED;
}

export function useAcknowledgeNotification() {
    const { t } = useTranslation();
    const [removeNotification, { isLoading, originalArgs }] = useRemoveUserNotificationMutation();

    const acknowledge = useCallback(
        async (notificationId: string) => {
            try {
                await removeNotification(notificationId).unwrap();
                dispatchMessage({ content: t('Notification has been acknowledged'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to acknowledge notification'), type: 'error' });
            }
        },
        [removeNotification, t],
    );

    return { acknowledge, acknowledgingId: isLoading ? originalArgs : undefined };
}
