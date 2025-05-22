import { BellOutlined, CloseOutlined } from '@ant-design/icons';
import { Badge, Button, Dropdown, Flex, type MenuProps, Space, theme, Typography } from 'antd';
import type { TFunction } from 'i18next';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { type NavigateFunction, useNavigate } from 'react-router';

import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import {
    useGetNotificationsQuery,
    useRemoveNotificationMutation,
} from '@/store/features/notifications/notifications-api-slice';
import { NotificationContract } from '@/types/notifications/notification.contract';

import styles from './notifications.module.scss';

export function Notifications() {
    const {
        token: { colorPrimary },
    } = theme.useToken();
    const { t } = useTranslation();
    const navigate = useNavigate();

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
        (
            notification: NotificationContract,
            navigate: NavigateFunction,
            t: TFunction,
            handleRemoveNotification: (id: string) => void,
        ) => {
            const navigatePath = '/';
            return {
                key: notification.id,
                label: (
                    <Flex>
                        <Typography.Text>
                            {t('{{name}}', {
                                name: notification.event.name,
                            })}
                        </Typography.Text>
                    </Flex>
                ),
                extra: (
                    <Button
                        type="link"
                        onClick={(event) => {
                            event.stopPropagation();
                            handleRemoveNotification(notification.id);
                        }}
                    >
                        <CloseOutlined />
                    </Button>
                ),
                onClick: () => navigate(navigatePath),
            };
        },
        [],
    );

    const notificationItems = useMemo(() => {
        const items = notifications?.map((notification) =>
            createNotificationItem(notification, navigate, t, handleRemoveNotification),
        );

        return items ?? [];
    }, [notifications, createNotificationItem, navigate, t, handleRemoveNotification]);

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
