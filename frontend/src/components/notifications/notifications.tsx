import { BellOutlined, CloseOutlined } from '@ant-design/icons';
import { Badge, Button, Dropdown, Flex, type MenuProps, Space, theme, Typography } from 'antd';
import type { TFunction } from 'i18next';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, type NavigateFunction, useNavigate } from 'react-router';

import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import {
    useGetNotificationsQuery,
    useRemoveNotificationMutation,
} from '@/store/features/notifications/notifications-api-slice';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import { Notification, NotificationTypes } from '@/types/notifications/notification.contract';
import { DecisionStatus } from '@/types/roles';
import {
    getNotificationDataOutput,
    getNotificationDataProduct,
    getNotificationDataset,
    getNotificationUser,
} from '@/utils/notification.helper';

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

    const createItem = useCallback(
        (
            userNotification: Notification,
            navigate: NavigateFunction,
            t: TFunction,
            handleRemoveNotification: (id: string) => void,
        ) => {
            let description, navigatePath;

            switch (userNotification.notification_type) {
                case NotificationTypes.DataProductDatasetNotification:
                    switch (userNotification.notification_origin) {
                        case DecisionStatus.Approved:
                            description = (
                                <Typography.Text>
                                    {t('The data product')}{' '}
                                    <Link
                                        onClick={(e) => e.stopPropagation()}
                                        to={createDataProductIdPath(userNotification.data_product_id)}
                                    >
                                        {getNotificationDataProduct(userNotification)}
                                    </Link>{' '}
                                    {t('has been granted read access to the')}{' '}
                                    <Link
                                        onClick={(e) => e.stopPropagation()}
                                        to={createDatasetIdPath(userNotification.dataset_id)}
                                    >
                                        {getNotificationDataset(userNotification)}
                                    </Link>{' '}
                                    {t('dataset')}
                                </Typography.Text>
                            );
                            break;
                        case DecisionStatus.Denied:
                            description = (
                                <Typography.Text>
                                    {t('The data product')}{' '}
                                    <Link
                                        onClick={(e) => e.stopPropagation()}
                                        to={createDataProductIdPath(userNotification.data_product_id)}
                                    >
                                        {getNotificationDataProduct(userNotification)}
                                    </Link>{' '}
                                    {t('has been denied read access to the')}{' '}
                                    <Link
                                        onClick={(e) => e.stopPropagation()}
                                        to={createDatasetIdPath(userNotification.dataset_id)}
                                    >
                                        {getNotificationDataset(userNotification)}
                                    </Link>{' '}
                                    {t('dataset')}
                                </Typography.Text>
                            );
                            break;
                    }
                    navigatePath = createDatasetIdPath(userNotification.dataset_id, DatasetTabKeys.DataProduct);
                    break;

                case NotificationTypes.DataOutputDatasetNotification:
                    switch (userNotification.notification_origin) {
                        case DecisionStatus.Approved:
                            description = (
                                <Typography.Text>
                                    {t('The data output')}{' '}
                                    <Link
                                        onClick={(e) => e.stopPropagation()}
                                        to={createDataOutputIdPath(
                                            userNotification.data_output_id,
                                            userNotification.data_product_id,
                                        )}
                                    >
                                        {getNotificationDataOutput(userNotification)}
                                    </Link>{' '}
                                    {t('has been granted a link to the')}{' '}
                                    <Link
                                        onClick={(e) => e.stopPropagation()}
                                        to={createDatasetIdPath(userNotification.dataset_id)}
                                    >
                                        {getNotificationDataset(userNotification)}
                                    </Link>{' '}
                                    {t('dataset')}
                                </Typography.Text>
                            );
                            break;
                        case DecisionStatus.Denied:
                            description = (
                                <Typography.Text>
                                    {t('The data output')}{' '}
                                    <Link
                                        onClick={(e) => e.stopPropagation()}
                                        to={createDataOutputIdPath(
                                            userNotification.data_output_id,
                                            userNotification.data_product_id,
                                        )}
                                    >
                                        {getNotificationDataOutput(userNotification)}
                                    </Link>{' '}
                                    {t('has been denied a link to the')}{' '}
                                    <Link
                                        onClick={(e) => e.stopPropagation()}
                                        to={createDatasetIdPath(userNotification.dataset_id)}
                                    >
                                        {getNotificationDataset(userNotification)}
                                    </Link>{' '}
                                    {t('dataset')}
                                </Typography.Text>
                            );
                            break;
                    }
                    navigatePath = createDatasetIdPath(userNotification.dataset_id, DatasetTabKeys.DataOutput);
                    break;

                case NotificationTypes.DataProductMembershipNotification:
                    switch (userNotification.notification_origin) {
                        case DecisionStatus.Approved:
                            description = (
                                <Typography.Text>
                                    {t('{{name}} has been granted the role of {{role}} in the team of the', {
                                        name: getNotificationUser(userNotification),
                                        role: userNotification.membership_role,
                                    })}{' '}
                                    <Link
                                        onClick={(e) => e.stopPropagation()}
                                        to={createDataProductIdPath(userNotification.data_product_id)}
                                    >
                                        {getNotificationDataProduct(userNotification)}
                                    </Link>{' '}
                                    {t('data product')}
                                </Typography.Text>
                            );
                            break;
                        case DecisionStatus.Denied:
                            description = (
                                <Typography.Text>
                                    {t('{{name}} has been denied the role of {{role}} in the team of the', {
                                        name: getNotificationUser(userNotification),
                                        role: userNotification.membership_role,
                                    })}{' '}
                                    <Link
                                        onClick={(e) => e.stopPropagation()}
                                        to={createDataProductIdPath(userNotification.data_product_id)}
                                    >
                                        {getNotificationDataProduct(userNotification)}
                                    </Link>{' '}
                                    {t('data product')}
                                </Typography.Text>
                            );
                            break;
                    }
                    navigatePath = createDataProductIdPath(userNotification.data_product_id, DataProductTabKeys.Team);
                    break;
            }

            return {
                key: userNotification.id,
                label: <Flex>{description}</Flex>,
                extra: (
                    <Button
                        type="link"
                        onClick={(event) => {
                            event.stopPropagation();
                            handleRemoveNotification(userNotification.id);
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
        const notificationCreatedItems = notifications?.map((action) =>
            createItem({ ...action }, navigate, t, handleRemoveNotification),
        );
        return notificationCreatedItems ?? [];
    }, [notifications, createItem, navigate, t, handleRemoveNotification]);

    const items: MenuProps['items'] = [
        {
            type: 'group',
            label: notificationItems?.length > 0 ? t('Notifications') : t('No notifications available'),
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
