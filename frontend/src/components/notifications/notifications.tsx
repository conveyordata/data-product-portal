import { BellOutlined, CheckOutlined } from '@ant-design/icons';
import { Badge, Button, Flex, Popover, Tag, Typography, theme } from 'antd';
import { type ReactNode, useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { EmptyState, emptyStateQueryProps, isAwaitingData } from '@/components/empty-state/empty-state.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import {
    type GetUserNotificationsResponseItem,
    useGetUserNotificationsQuery,
    useRemoveAllUserNotificationsMutation,
    useRemoveUserNotificationMutation,
} from '@/store/api/services/generated/usersNotificationsApi.ts';
import { EventType } from '@/types/events/event-types.ts';
import { formatDateToNowFromUTCString } from '@/utils/date.helper';
import { dispatchMessage } from '@/utils/feedback.ts';
import { AnnouncementNotification } from './announcement-notification';
import { NotificationDescription } from './notification-description';
import styles from './notifications.module.scss';

const MAX_ITEMS_DEFAULT = 10;

export function Notifications() {
    const {
        token: { colorError },
    } = theme.useToken();
    const { t } = useTranslation();

    const notificationsQuery = useGetUserNotificationsQuery();
    const { data: { notifications = [] } = {} } = notificationsQuery;

    const [removeNotification] = useRemoveUserNotificationMutation();
    const [removeAllNotifications] = useRemoveAllUserNotificationsMutation();
    const [maxItems, setMaxItems] = useState(MAX_ITEMS_DEFAULT);

    const handleRemoveNotification = useCallback(
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

    const handleRemoveAllNotifications = useCallback(async () => {
        try {
            await removeAllNotifications().unwrap();
            dispatchMessage({ content: t('Notifications acknowledged'), type: 'success' });
        } catch (_error) {
            dispatchMessage({ content: t('Failed to acknowledge notifications'), type: 'error' });
        }
    }, [removeAllNotifications, t]);

    const createNotificationItem = useCallback(
        (
            notification: GetUserNotificationsResponseItem,
            showActor: boolean,
            handleRemoveNotification: (id: string) => void,
            idx: number,
        ): ReactNode => {
            const event = notification.event;

            return (
                <Flex key={notification.id} justify="space-between" className={styles.width}>
                    <Flex vertical className={styles.width}>
                        {showActor && (
                            <Flex className={idx === 0 ? '' : styles.marginTop}>
                                <Tag color="default">
                                    {event.actor
                                        ? `${event.actor.first_name} ${event.actor.last_name}`
                                        : (event.deleted_actor_identifier ?? '')}
                                    , {formatDateToNowFromUTCString(notification.event.created_on)}:
                                </Tag>
                            </Flex>
                        )}
                        <Flex justify="space-between" className={styles.width}>
                            <NotificationDescription record={notification.event} />
                            <Button
                                className={styles.closeButton}
                                type="text"
                                icon={<CheckOutlined />}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleRemoveNotification(notification.id);
                                }}
                            />
                        </Flex>
                    </Flex>
                </Flex>
            );
        },
        [],
    );

    const handleLoadMore = useCallback(() => {
        setMaxItems((prev) => prev + MAX_ITEMS_DEFAULT);
    }, []);

    const [announcementNotifications, requestNotifications] = useMemo(() => {
        const isAnnouncement = (notification: GetUserNotificationsResponseItem) =>
            notification.event.name === EventType.ANNOUNCEMENT_CREATED;
        return [notifications.filter(isAnnouncement), notifications.filter((n) => !isAnnouncement(n))];
    }, [notifications]);

    const createShowMoreItem = useCallback(
        (excessLength: number) => (
            <Flex key="show-more-indicator" className={styles.notificationItem}>
                <Button
                    className={styles.closeButton}
                    type="link"
                    onClick={(event) => {
                        event.stopPropagation();
                        handleLoadMore();
                    }}
                >
                    <Typography.Text type="secondary">
                        {t('... {{count}} more items', { count: excessLength })}
                    </Typography.Text>
                </Button>
            </Flex>
        ),
        [handleLoadMore, t],
    );

    const requestItems = useMemo(() => {
        const slicedItems = requestNotifications.slice(0, maxItems).map((notification, idx) => {
            const prev = requestNotifications[idx - 1];
            const sameActorAsPrevious = idx > 0 && prev.event.actor_id === notification.event.actor_id;

            return createNotificationItem(notification, !sameActorAsPrevious, handleRemoveNotification, idx);
        });

        const excessLength = requestNotifications.length - maxItems;
        if (excessLength > 0) slicedItems.push(createShowMoreItem(excessLength));

        return slicedItems;
    }, [requestNotifications, createNotificationItem, handleRemoveNotification, maxItems, createShowMoreItem]);

    const announcementItems = useMemo(() => {
        const slicedItems = announcementNotifications
            .slice(0, maxItems)
            .map((notification) => (
                <AnnouncementNotification
                    key={notification.id}
                    notification={notification}
                    onAcknowledge={handleRemoveNotification}
                />
            ));

        const excessLength = announcementNotifications.length - maxItems;
        if (excessLength > 0) slicedItems.push(createShowMoreItem(excessLength));

        return slicedItems;
    }, [announcementNotifications, handleRemoveNotification, maxItems, createShowMoreItem]);

    const notificationItems = [
        { key: 'requests', title: t('Requests'), items: requestItems },
        { key: 'announcements', title: t('Announcements'), items: announcementItems },
    ]
        .filter(({ items }) => items.length > 0)
        .map(({ key, title, items }) => (
            <Flex key={key} vertical gap="small">
                <Typography.Text type="secondary" strong>
                    {title}
                </Typography.Text>
                {items}
            </Flex>
        ));

    const header = useMemo(() => {
        if (notificationItems?.length > 0) {
            return (
                <Flex justify="space-between" align="center" className={styles.notificationLabel}>
                    <Typography.Title level={4}>{t('Notifications')}</Typography.Title>{' '}
                    <Button onClick={handleRemoveAllNotifications}>{t('Acknowledge all')}</Button>
                </Flex>
            );
        }

        if (isAwaitingData(notificationsQuery)) return <LoadingSpinner />;

        return (
            <EmptyState
                size="small"
                icon={<BellOutlined />}
                title={t('No notifications')}
                description={t('Updates about your requests and the things you own appear here.')}
                {...emptyStateQueryProps(notificationsQuery)}
            />
        );
    }, [notificationItems?.length, t, handleRemoveAllNotifications, notificationsQuery]);

    return (
        <Flex>
            <Badge
                count={(notifications ?? []).length}
                showZero={false}
                color={colorError}
                style={{ fontSize: 10 }}
                size="small"
            >
                <Popover
                    content={
                        <div>
                            {header}
                            <Flex vertical gap="middle" className={styles.notificationItems}>
                                {notificationItems}
                            </Flex>
                        </div>
                    }
                    classNames={{ content: styles.notificationBody }}
                    trigger="hover"
                    placement="bottom"
                >
                    <Button shape="circle" className={styles.iconButton} icon={<BellOutlined />} />
                </Popover>
            </Badge>
        </Flex>
    );
}
