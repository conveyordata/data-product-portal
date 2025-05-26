import { BellOutlined, CloseOutlined } from '@ant-design/icons';
import { Badge, Button, Dropdown, Flex, type MenuProps, Space, Tag, theme } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import {
    useGetNotificationsQuery,
    useRemoveNotificationMutation,
} from '@/store/features/notifications/notifications-api-slice';
import { NotificationContract } from '@/types/notifications/notification.contract';
import { formatDateToNow } from '@/utils/date.helper';

import { NotificationDescription } from './notification-description';
import styles from './notifications.module.scss';

export function Notifications() {
    const {
        token: { colorPrimary },
    } = theme.useToken();
    const { t } = useTranslation();

    const { data: notifications } = useGetNotificationsQuery();

    const [removeNotification] = useRemoveNotificationMutation();

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
                                    {formatDateToNow(notification.event.created_on)}
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

        return notifications.map((notification, idx) => {
            const prev = notifications[idx - 1];
            const sameActorAsPrevious = idx > 0 && prev.event.actor.id === notification.event.actor.id;

            return createNotificationItem(notification, !sameActorAsPrevious, handleRemoveNotification);
        });
    }, [notifications, createNotificationItem, handleRemoveNotification]);

    const items: MenuProps['items'] = [
        {
            type: 'group',
            label: notificationItems?.length > 0 ? t('Notifications') : t('You currently have no notifications'),
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
