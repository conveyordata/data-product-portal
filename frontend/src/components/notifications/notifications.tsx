import { BellOutlined, ExportOutlined } from '@ant-design/icons';
import { Badge, Button, Dropdown, Flex, type MenuProps, Space, Tag, theme, Typography } from 'antd';
import type { TFunction } from 'i18next';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, type NavigateFunction, useNavigate } from 'react-router';

import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import {
    useGetNotificationsQuery,
    useGetPendingActionNotificationsQuery,
} from '@/store/features/notifications/notifications-api-slice';
import { DataOutputDatasetLinkStatus } from '@/types/data-output-dataset';
import { DataProductDatasetLinkStatus } from '@/types/data-product-dataset';
import { DataProductMembershipStatus } from '@/types/data-product-membership';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import { NotificationModel, NotificationTypes } from '@/types/notifications/notification.contract';
import { formatDateToNow } from '@/utils/date.helper';

import styles from './notifications.module.scss';

export function Notifications() {
    const {
        token: { colorPrimary },
    } = theme.useToken();
    const { t } = useTranslation();
    const navigate = useNavigate();

    const { data: notifications } = useGetNotificationsQuery();
    const { data: pendingActions } = useGetPendingActionNotificationsQuery();

    const createItem = useCallback((userNotification: NotificationModel, navigate: NavigateFunction, t: TFunction) => {
        let link, description, navigatePath;

        switch (userNotification.notification.configuration_type) {
            case NotificationTypes.DataProductDatasetNotification:
                link = createDataProductIdPath(userNotification.notification.reference.data_product_id);
                switch (userNotification.notification.reference.status) {
                    case DataProductDatasetLinkStatus.Approved:
                        description = (
                            <div className={styles.notification}>
                                <div className={styles.notificationHeader}>
                                    <div className={styles.notificationTitle}>
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.reference.data_product.name}
                                        </Link>{' '}
                                        <Typography.Text className={styles.notificationMessage}>
                                            {t('data product:')}
                                        </Typography.Text>
                                    </div>

                                    <Tag color="blue" className={styles.timestampTag}>
                                        {userNotification.notification.reference.approved_on
                                            ? formatDateToNow(userNotification.notification.reference.approved_on)
                                            : undefined}
                                    </Tag>
                                    <ExportOutlined />
                                </div>

                                <div className={styles.notificationContent}>
                                    <Typography.Text className={styles.notificationMessage}>
                                        {t('Read access granted to dataset:')}{' '}
                                        <Link
                                            onClick={(e) => e.stopPropagation()}
                                            to={createDatasetIdPath(userNotification.notification.reference.dataset_id)}
                                        >
                                            {userNotification.notification.reference.dataset.name}
                                        </Link>
                                    </Typography.Text>
                                </div>
                            </div>
                        );
                        break;
                    case DataProductDatasetLinkStatus.Denied:
                        description = (
                            <div className={styles.notification}>
                                <div className={styles.notificationHeader}>
                                    <div>
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.reference.data_product.name}
                                        </Link>{' '}
                                        <Typography.Text className={styles.notificationMessage}>
                                            {t('data product:')}
                                        </Typography.Text>
                                    </div>

                                    <Tag color="blue" className={styles.timestampTag}>
                                        {userNotification.notification.reference.denied_on
                                            ? formatDateToNow(userNotification.notification.reference.denied_on)
                                            : undefined}
                                    </Tag>
                                    <ExportOutlined />
                                </div>

                                <div className={styles.notificationContent}>
                                    <Typography.Text className={styles.notificationMessage}>
                                        {t('Read access denied to dataset:')}{' '}
                                        <Link
                                            onClick={(e) => e.stopPropagation()}
                                            to={createDatasetIdPath(userNotification.notification.reference.dataset_id)}
                                        >
                                            {userNotification.notification.reference.dataset.name}
                                        </Link>
                                    </Typography.Text>
                                </div>
                            </div>
                        );
                        break;
                }
                navigatePath = createDatasetIdPath(
                    userNotification.notification.reference.dataset_id,
                    DatasetTabKeys.DataProduct,
                );
                break;

            case NotificationTypes.DataOutputDatasetNotification:
                link = createDataOutputIdPath(
                    userNotification.notification.reference.data_output_id,
                    userNotification.notification.reference.data_output.owner_id,
                );
                switch (userNotification.notification.reference.status) {
                    case DataOutputDatasetLinkStatus.Approved:
                        description = (
                            <div className={styles.notification}>
                                <div className={styles.notificationHeader}>
                                    <div>
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.reference.data_output.name}
                                        </Link>{' '}
                                        <Typography.Text className={styles.notificationMessage}>
                                            {t('data output:')}
                                        </Typography.Text>
                                    </div>

                                    <Tag color="blue" className={styles.timestampTag}>
                                        {userNotification.notification.reference.approved_on
                                            ? formatDateToNow(userNotification.notification.reference.approved_on)
                                            : undefined}
                                    </Tag>
                                    <ExportOutlined />
                                </div>

                                <div className={styles.notificationContent}>
                                    <Typography.Text className={styles.notificationMessage}>
                                        {t('Linking approved for dataset:')}{' '}
                                        <Link
                                            onClick={(e) => e.stopPropagation()}
                                            to={createDatasetIdPath(userNotification.notification.reference.dataset_id)}
                                        >
                                            {userNotification.notification.reference.dataset.name}
                                        </Link>
                                    </Typography.Text>
                                </div>
                            </div>
                        );
                        break;
                    case DataOutputDatasetLinkStatus.Denied:
                        description = (
                            <div className={styles.notification}>
                                <div className={styles.notificationHeader}>
                                    <div>
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.reference.data_output.name}
                                        </Link>{' '}
                                        <Typography.Text className={styles.notificationMessage}>
                                            {t('data output:')}
                                        </Typography.Text>
                                    </div>

                                    <Tag color="blue" className={styles.timestampTag}>
                                        {userNotification.notification.reference.denied_on
                                            ? formatDateToNow(userNotification.notification.reference.denied_on)
                                            : undefined}
                                    </Tag>
                                    <ExportOutlined />
                                </div>

                                <div className={styles.notificationContent}>
                                    <Typography.Text className={styles.notificationMessage}>
                                        {t('Linking denied for dataset:')}{' '}
                                        <Link
                                            onClick={(e) => e.stopPropagation()}
                                            to={createDatasetIdPath(userNotification.notification.reference.dataset_id)}
                                        >
                                            {userNotification.notification.reference.dataset.name}
                                        </Link>
                                    </Typography.Text>
                                </div>
                            </div>
                        );
                        break;
                }
                navigatePath = createDatasetIdPath(
                    userNotification.notification.reference.dataset_id,
                    DatasetTabKeys.DataOutput,
                );
                break;

            case NotificationTypes.DataProductMembershipNotification:
                link = createDataProductIdPath(userNotification.notification.reference.data_product_id);
                switch (userNotification.notification.reference.status) {
                    case DataProductMembershipStatus.Approved:
                        description = (
                            <div className={styles.notification}>
                                <div className={styles.notificationHeader}>
                                    <div>
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.reference.data_product.name}
                                        </Link>{' '}
                                        <Typography.Text className={styles.notificationMessage}>
                                            {t('data product:')}
                                        </Typography.Text>
                                    </div>

                                    <Tag color="blue" className={styles.timestampTag}>
                                        {userNotification.notification.reference.approved_on
                                            ? formatDateToNow(userNotification.notification.reference.approved_on)
                                            : undefined}
                                    </Tag>
                                    <ExportOutlined />
                                </div>

                                <div className={styles.notificationContent}>
                                    <Typography.Text className={styles.notificationMessage}>
                                        {t('You have been granted the role of {{role}}', {
                                            role: userNotification.notification.reference.role,
                                        })}{' '}
                                    </Typography.Text>
                                </div>
                            </div>
                        );
                        break;
                    case DataProductMembershipStatus.Denied:
                        description = (
                            <div className={styles.notification}>
                                <div className={styles.notificationHeader}>
                                    <div>
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.reference.data_product.name}
                                        </Link>{' '}
                                        <Typography.Text className={styles.notificationMessage}>
                                            {t('data product:')}
                                        </Typography.Text>
                                    </div>

                                    <Tag color="blue" className={styles.timestampTag}>
                                        {userNotification.notification.reference.denied_on
                                            ? formatDateToNow(userNotification.notification.reference.denied_on)
                                            : undefined}
                                    </Tag>
                                    <ExportOutlined />
                                </div>

                                <div className={styles.notificationContent}>
                                    <Typography.Text className={styles.notificationMessage}>
                                        {t('You have been denied the role of {{role}}', {
                                            role: userNotification.notification.reference.role,
                                        })}{' '}
                                    </Typography.Text>
                                </div>
                            </div>
                        );
                        break;
                }
                navigatePath = createDataProductIdPath(
                    userNotification.notification.reference.data_product_id,
                    DataProductTabKeys.Team,
                );
                break;

            default:
                return null;
        }

        return {
            key: userNotification.id,
            label: <div className={styles.notificationItem}>{description}</div>,
            onClick: () => navigate(navigatePath),
        };
    }, []);

    const handleRedirectHome = () => {
        navigate('/');
    };

    const notificationItems = useMemo(() => {
        const notificationCreatedItems = notifications?.map((action) => createItem({ ...action }, navigate, t));
        return notificationCreatedItems ?? [];
    }, [notifications, createItem, navigate, t]);

    const notificationItemCount = useMemo(() => notificationItems?.length || 0, [notificationItems]);

    const requestItemCount = useMemo(() => pendingActions?.length || 0, [pendingActions]);

    const items: MenuProps['items'] = [
        {
            type: 'group',
            label: (
                <div className={styles.notificationTitlebar}>
                    <Flex>
                        <Typography.Title level={4}>Notifications</Typography.Title>{' '}
                        <Badge count={notificationItemCount} color="gray" size="small" />
                    </Flex>
                    {requestItemCount != 0 && (
                        <Button type="link" value="pendingRequests" onClick={handleRedirectHome}>
                            <strong> {t('View requests')}</strong>
                            <Badge count={requestItemCount} color="gray" size="small" />
                        </Button>
                    )}
                </div>
            ),
            children: notificationItems,
        },
    ];

    return (
        <Flex>
            <Badge
                count={notificationItemCount + requestItemCount}
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
