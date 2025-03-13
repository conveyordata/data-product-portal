import { BellOutlined, ExportOutlined } from '@ant-design/icons';
import { Badge, Button, Dropdown, Flex, type MenuProps, Space, theme, Typography } from 'antd';
import type { TFunction } from 'i18next';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, type NavigateFunction, useNavigate } from 'react-router';

import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { useGetNotificationsQuery } from '@/store/features/notifications/notifications-api-slice';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import { NotificationModel, NotificationTypes } from '@/types/notifications/notification.contract';

import styles from './notifications.module.scss';

export function Notifications() {
    const {
        token: { colorPrimary },
    } = theme.useToken();
    const { t } = useTranslation();
    const navigate = useNavigate();

    const { data: notifications } = useGetNotificationsQuery();

    const createItem = useCallback((userNotification: NotificationModel, navigate: NavigateFunction, t: TFunction) => {
        let link, description, navigatePath;

        switch (userNotification.notification.configuration_type) {
            case NotificationTypes.DataProductDataset:
                link = createDataProductIdPath(userNotification.notification.data_product_dataset.data_product_id);
                description = (
                    <Typography.Text>
                        {t('{{name}}, on behalf of data product', {
                            name: userNotification.notification.data_product_dataset.requested_by?.first_name,
                        })}{' '}
                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                            {userNotification.notification.data_product_dataset.data_product.name}
                        </Link>{' '}
                        {t('requests read access to dataset')}{' '}
                        <Link
                            onClick={(e) => e.stopPropagation()}
                            to={createDatasetIdPath(userNotification.notification.data_product_dataset.dataset_id)}
                        >
                            {userNotification.notification.data_product_dataset.dataset.name}
                        </Link>
                    </Typography.Text>
                );
                navigatePath = createDatasetIdPath(
                    userNotification.notification.data_product_dataset.dataset_id,
                    DatasetTabKeys.DataProduct,
                );
                break;

            case NotificationTypes.DataOutputDataset:
                link = createDataOutputIdPath(
                    userNotification.notification.data_output_dataset.data_output_id,
                    userNotification.notification.data_output_dataset.data_output.owner_id,
                );
                description = (
                    <Typography.Text>
                        {t('{{name}}, on behalf of data output', {
                            name: userNotification.notification.data_output_dataset.requested_by?.first_name,
                        })}{' '}
                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                            {userNotification.notification.data_output_dataset.data_output.name}
                        </Link>{' '}
                        {t('requests a link to dataset')}{' '}
                        <Link
                            onClick={(e) => e.stopPropagation()}
                            to={createDatasetIdPath(userNotification.notification.data_output_dataset.dataset_id)}
                        >
                            {userNotification.notification.data_output_dataset.dataset.name}
                        </Link>
                    </Typography.Text>
                );
                navigatePath = createDatasetIdPath(
                    userNotification.notification.data_output_dataset.dataset_id,
                    DatasetTabKeys.DataOutput,
                );
                break;

            case NotificationTypes.DataProductMembership:
                link = createDataProductIdPath(userNotification.notification.data_product_membership.data_product_id);
                description = (
                    <Typography.Text>
                        {t('{{name}} would like to join the data product', {
                            name: userNotification.notification.data_product_membership.user?.first_name,
                        })}{' '}
                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                            {userNotification.notification.data_product_membership.data_product.name}
                        </Link>{' '}
                        {t('team')}{' '}
                    </Typography.Text>
                );
                navigatePath = createDataProductIdPath(
                    userNotification.notification.data_product_membership.data_product_id,
                    DataProductTabKeys.Team,
                );
                break;

            default:
                return null;
        }

        return {
            key: userNotification.id,
            label: <Flex>{description}</Flex>,
            extra: <ExportOutlined />,
            onClick: () => navigate(navigatePath),
        };
    }, []);

    const notificationItems = useMemo(() => {
        const notificationCreatedItems = notifications?.map((action) => createItem({ ...action }, navigate, t));
        return notificationCreatedItems ?? [];
    }, [notifications, createItem, navigate, t]);

    const items: MenuProps['items'] = [
        {
            type: 'group',
            label: notificationItems?.length > 0 ? t('Pending actions') : t('No pending actions'),
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
