import { BellOutlined, CloseOutlined } from '@ant-design/icons';
import { Badge, Button, Dropdown, Flex, type MenuProps, Space, Tag, theme, Typography } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import {
    useGetNotificationsQuery,
    useRemoveAllNotificationsMutation,
    useRemoveNotificationMutation,
} from '@/store/features/notifications/notifications-api-slice';
import { NotificationContract } from '@/types/notifications/notification.contract';
import { formatDateToNow } from '@/utils/date.helper';

import { NotificationDescription } from './notification-description';
import styles from './notifications.module.scss';

const MAX_ITEMS = 15;

export function Notifications() {
    const {
        token: { colorPrimary },
    } = theme.useToken();
    const { t } = useTranslation();

    const { data: notifications } = useGetNotificationsQuery();

    const [removeNotification] = useRemoveNotificationMutation();
    const [removeAllNotifications] = useRemoveAllNotificationsMutation();

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
        (notification: NotificationContract, showActor: boolean, handleRemoveNotification: (id: string) => void) => {
            return {
                key: notification.id,
                className: showActor ? styles.notificationItemWithActor : styles.notificationItem,
                label: (
                    <Flex vertical className={styles.notificationContainer}>
                        {showActor && (
                            <Flex className={styles.notificationTag}>
                                <Tag color="default">
                                    {notification.event.actor.first_name} {notification.event.actor.last_name},{' '}
                                    {formatDateToNow(notification.event.created_on)}:
                                </Tag>
                            </Flex>
                        )}

                        <NotificationDescription record={notification.event} />
                    </Flex>
                ),
                extra: (
                    <Button
                        className={styles.closeButton}
                        type="link"
                        onClick={(event) => {
                            event.stopPropagation();
                            handleRemoveNotification(notification.id);
                        }}
                    >
                        <CloseOutlined />
                    </Button>
                ),
            };
        },
        [],
    );

    const notificationItems = useMemo(() => {
        if (!notifications || notifications.length === 0) return [];

        const slicedItems = notifications.slice(0, MAX_ITEMS).map((notification, idx) => {
            const prev = notifications[idx - 1];
            const sameActorAsPrevious = idx > 0 && prev.event.actor.id === notification.event.actor.id;

            return createNotificationItem(notification, !sameActorAsPrevious, handleRemoveNotification);
        });

        const excessLength = notifications.length - MAX_ITEMS;

        if (excessLength > 0) {
            slicedItems.push({
                key: 'more-indicator',
                className: '',
                label: (
                    <Typography.Text type="secondary">
                        {excessLength === 1
                            ? t('... {{count}} more item', { count: excessLength })
                            : t('... {{count}} more items', { count: excessLength })}
                    </Typography.Text>
                ),
                extra: <></>,
            });
        }

        return slicedItems;
    }, [notifications, createNotificationItem, handleRemoveNotification, t]);

    const items: MenuProps['items'] = [
        {
            type: 'group',
            label:
                notificationItems?.length > 0 ? (
                    <Flex justify="space-between" align="center">
                        <Typography.Title level={4} className={styles.marginBottom}>
                            {t('Notifications')}
                        </Typography.Title>{' '}
                        <Button onClick={handleRemoveAllNotifications} className={styles.marginBottom}>
                            {t('Delete all')}
                        </Button>
                    </Flex>
                ) : (
                    t('You currently have no notifications')
                ),
            children: notificationItems,
        },
    ];

    return (
        <Flex>
            <Badge
                count={notificationItems?.length}
                showZero={false}
                color={colorPrimary}
                style={{ fontSize: 10 }}
                size="small"
            >
                <Dropdown
                    placement={'bottomRight'}
                    menu={{
                        items,
                    }}
                    trigger={['click']}
                >
                    <Space>
                        <Button shape={'circle'} className={styles.iconButton} icon={<BellOutlined />} />
                    </Space>
                </Dropdown>
            </Badge>
        </Flex>
    );
}
