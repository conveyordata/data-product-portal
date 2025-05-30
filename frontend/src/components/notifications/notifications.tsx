import { BellOutlined, CloseOutlined } from '@ant-design/icons';
import { Badge, Button, Flex, Popover, Space, Tag, theme, Typography } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import {
    useGetNotificationsQuery,
    useRemoveAllNotificationsMutation,
    useRemoveNotificationMutation,
} from '@/store/features/notifications/notifications-api-slice';
import { NotificationContract } from '@/types/notifications/notification.contract';
import { formatDateToNowFromUTCString } from '@/utils/date.helper';

import { NotificationDescription } from './notification-description';
import styles from './notifications.module.scss';

const MAX_ITEMS_DEFAULT = 10;

export function Notifications() {
    const {
        token: { colorPrimary },
    } = theme.useToken();
    const { t } = useTranslation();

    const { data: notifications } = useGetNotificationsQuery();

    const [removeNotification] = useRemoveNotificationMutation();
    const [removeAllNotifications] = useRemoveAllNotificationsMutation();
    const [maxItems, setMaxItems] = useState(MAX_ITEMS_DEFAULT);

    const handleRemoveNotification = useCallback(
        async (notificationId: string) => {
            try {
                await removeNotification(notificationId).unwrap();
                dispatchMessage({ content: t('Notification has been removed'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to remove notification'), type: 'error' });
            }
        },
        [removeNotification, t],
    );

    const handleRemoveAllNotifications = useCallback(async () => {
        try {
            await removeAllNotifications().unwrap();
            dispatchMessage({ content: t('Notifications removed'), type: 'success' });
        } catch (_error) {
            dispatchMessage({ content: t('Failed to remove notifications'), type: 'error' });
        }
    }, [removeAllNotifications, t]);

    const createNotificationItem = useCallback(
        (
            notification: NotificationContract,
            showActor: boolean,
            handleRemoveNotification: (id: string) => void,
            idx: number,
        ): React.ReactNode => {
            return (
                <Flex key={notification.id} justify="space-between" className={styles.width}>
                    <Flex vertical className={styles.width}>
                        {showActor && (
                            <Flex className={idx === 0 ? '' : styles.marginTop}>
                                <Tag color="default">
                                    {notification.event.actor.first_name} {notification.event.actor.last_name},{' '}
                                    {formatDateToNowFromUTCString(notification.event.created_on)}:
                                </Tag>
                            </Flex>
                        )}
                        <Flex justify="space-between" className={styles.width}>
                            <NotificationDescription record={notification.event} />
                            <Button
                                className={styles.closeButton}
                                type="text"
                                icon={<CloseOutlined />}
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

    const notificationItems = useMemo(() => {
        if (!notifications || notifications.length === 0) return [];

        const slicedItems = notifications.slice(0, maxItems).map((notification, idx) => {
            const prev = notifications[idx - 1];
            const sameActorAsPrevious = idx > 0 && prev.event.actor.id === notification.event.actor.id;

            return createNotificationItem(notification, !sameActorAsPrevious, handleRemoveNotification, idx);
        });

        const excessLength = notifications.length - maxItems;

        if (excessLength > 0) {
            slicedItems.push(
                <Flex key={'show-more-indicator'} className={styles.notificationItem}>
                    <Button
                        className={styles.closeButton}
                        type="link"
                        onClick={(event) => {
                            event.stopPropagation();
                            handleLoadMore();
                        }}
                    >
                        <Typography.Text type="secondary">
                            {excessLength === 1
                                ? t('... {{count}} more item', { count: excessLength })
                                : t('... {{count}} more items', { count: excessLength })}
                        </Typography.Text>
                    </Button>
                </Flex>,
            );
        }

        return slicedItems;
    }, [notifications, createNotificationItem, handleRemoveNotification, t, maxItems, handleLoadMore]);

    const header = useMemo(() => {
        if (notificationItems?.length > 0) {
            return (
                <Flex justify="space-between" align="center" className={styles.notificationLabel}>
                    <Typography.Title level={4}>{t('Notifications')}</Typography.Title>{' '}
                    <Button onClick={handleRemoveAllNotifications}>{t('Delete all')}</Button>
                </Flex>
            );
        }

        return (
            <Typography.Text className={styles.emptyLabel}>{t('You currently have no notifications')}</Typography.Text>
        );
    }, [notificationItems?.length, t, handleRemoveAllNotifications]);

    return (
        <Flex>
            <Badge
                count={(notifications ?? []).length}
                showZero={false}
                color={colorPrimary}
                style={{ fontSize: 10 }}
                size="small"
            >
                <Popover
                    content={
                        <div>
                            {header}
                            <Flex vertical className={styles.notificationItems}>
                                {notificationItems}
                            </Flex>
                        </div>
                    }
                    classNames={{ body: styles.notificationBody }}
                    trigger="click"
                    placement="bottomRight"
                >
                    <Space>
                        <Button shape={'circle'} className={styles.iconButton} icon={<BellOutlined />} />
                    </Space>
                </Popover>
            </Badge>
        </Flex>
    );
}
