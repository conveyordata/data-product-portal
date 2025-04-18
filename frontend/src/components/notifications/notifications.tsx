import { BellOutlined, CloseOutlined } from '@ant-design/icons';
import { Badge, Button, Dropdown, Flex, type MenuProps, Space, Tag, theme, Typography } from 'antd';
import type { TFunction } from 'i18next';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, type NavigateFunction, useNavigate } from 'react-router';

import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useGetDataOutputDatasetPendingActionsQuery } from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice';
import { useGetDataProductMembershipPendingActionsQuery } from '@/store/features/data-product-memberships/data-product-memberships-api-slice';
import { useGetDataProductDatasetPendingActionsQuery } from '@/store/features/data-products-datasets/data-products-datasets-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import {
    useGetNotificationsQuery,
    useRemoveNotificationMutation,
} from '@/store/features/notifications/notifications-api-slice';
import { DataOutputDatasetLinkStatus } from '@/types/data-output-dataset';
import { DataProductDatasetLinkStatus } from '@/types/data-product-dataset';
import { DataProductMembershipStatus } from '@/types/data-product-membership';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import { NotificationModel, NotificationTypes } from '@/types/notifications/notification.contract';
import { UserContract } from '@/types/users';
import { formatDateToNow } from '@/utils/date.helper';

import styles from './notifications.module.scss';

export function Notifications() {
    const {
        token: { colorPrimary },
    } = theme.useToken();
    const { t } = useTranslation();
    const navigate = useNavigate();

    const { data: notifications } = useGetNotificationsQuery();
    const { data: pendingActionsDatasets } = useGetDataProductDatasetPendingActionsQuery();
    const { data: pendingActionsDataOutputs } = useGetDataOutputDatasetPendingActionsQuery();
    const { data: pendingActionsDataProducts } = useGetDataProductMembershipPendingActionsQuery();

    const pendingActionsCount = useMemo(() => {
        const datasetsLength = pendingActionsDatasets?.length || 0;
        const dataOutputsLength = pendingActionsDataOutputs?.length || 0;
        const dataProductsLength = pendingActionsDataProducts?.length || 0;

        return datasetsLength + dataOutputsLength + dataProductsLength;
    }, [pendingActionsDatasets, pendingActionsDataOutputs, pendingActionsDataProducts]);

    const currentUser = useSelector(selectCurrentUser);
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
            userNotification: NotificationModel,
            navigate: NavigateFunction,
            t: TFunction,
            currentUser: UserContract | null,
            handleRemoveNotification: (id: string) => void,
        ) => {
            let link, description, navigatePath;

            switch (userNotification.notification.notification_type) {
                case NotificationTypes.DataProductDatasetNotification:
                    link = createDataProductIdPath(userNotification.notification.data_product_dataset.data_product_id);
                    switch (userNotification.notification.data_product_dataset.status) {
                        case DataProductDatasetLinkStatus.Approved:
                            description =
                                currentUser?.id ===
                                userNotification.notification.data_product_dataset.requested_by.id ? (
                                    <div className={styles.notification}>
                                        <div className={styles.notificationHeader}>
                                            <div className={styles.notificationTitle}>
                                                <Link onClick={(e) => e.stopPropagation()} to={link}>
                                                    {
                                                        userNotification.notification.data_product_dataset.data_product
                                                            .name
                                                    }
                                                </Link>{' '}
                                                <Typography.Text className={styles.notificationMessage}>
                                                    {t('data product:')}
                                                </Typography.Text>
                                            </div>

                                            <Tag color="blue" className={styles.timestampTag}>
                                                {userNotification.notification.data_product_dataset.approved_on
                                                    ? formatDateToNow(
                                                          userNotification.notification.data_product_dataset
                                                              .approved_on,
                                                      )
                                                    : undefined}
                                            </Tag>
                                            <Button
                                                type="text"
                                                size="small"
                                                style={{ padding: 0 }}
                                                onClick={() => handleRemoveNotification(userNotification.id)}
                                            >
                                                <CloseOutlined />
                                            </Button>
                                        </div>

                                        <div className={styles.notificationContent}>
                                            <Typography.Text className={styles.notificationMessage}>
                                                {t('Read access granted to dataset:')}{' '}
                                                <Link
                                                    onClick={(e) => e.stopPropagation()}
                                                    to={createDatasetIdPath(
                                                        userNotification.notification.data_product_dataset.dataset_id,
                                                    )}
                                                >
                                                    {userNotification.notification.data_product_dataset.dataset.name}
                                                </Link>
                                            </Typography.Text>
                                        </div>
                                    </div>
                                ) : (
                                    <div className={styles.notification}>
                                        <div className={styles.notificationHeader}>
                                            <div className={styles.notificationTitle}>
                                                <Link onClick={(e) => e.stopPropagation()} to={link}>
                                                    {
                                                        userNotification.notification.data_product_dataset.data_product
                                                            .name
                                                    }
                                                </Link>
                                                <Link
                                                    onClick={(e) => e.stopPropagation()}
                                                    to={createDatasetIdPath(
                                                        userNotification.notification.data_product_dataset.dataset_id,
                                                    )}
                                                >
                                                    {userNotification.notification.data_product_dataset.dataset.name}
                                                </Link>{' '}
                                                <Typography.Text className={styles.notificationMessage}>
                                                    {t('dataset:')}
                                                </Typography.Text>
                                            </div>
                                            <Tag color="blue" className={styles.timestampTag}>
                                                {userNotification.notification.data_product_dataset.approved_on
                                                    ? formatDateToNow(
                                                          userNotification.notification.data_product_dataset
                                                              .approved_on,
                                                      )
                                                    : undefined}{' '}
                                            </Tag>
                                            <Button
                                                type="text"
                                                size="small"
                                                style={{ padding: 0 }}
                                                onClick={() => handleRemoveNotification(userNotification.id)}
                                            >
                                                <CloseOutlined />
                                            </Button>
                                        </div>

                                        <div className={styles.notificationContent}>
                                            <Typography.Text className={styles.notificationMessage}>
                                                {t('Read access has been granted to data product:')}{' '}
                                                <Link onClick={(e) => e.stopPropagation()} to={link}>
                                                    {
                                                        userNotification.notification.data_product_dataset.data_product
                                                            .name
                                                    }
                                                </Link>{' '}
                                            </Typography.Text>
                                        </div>
                                    </div>
                                );
                            break;
                        case DataProductDatasetLinkStatus.Denied:
                            description =
                                currentUser?.id ===
                                userNotification.notification.data_product_dataset.requested_by.id ? (
                                    <div className={styles.notification}>
                                        <div className={styles.notificationHeader}>
                                            <div className={styles.notificationTitle}>
                                                <Link onClick={(e) => e.stopPropagation()} to={link}>
                                                    {
                                                        userNotification.notification.data_product_dataset.data_product
                                                            .name
                                                    }
                                                </Link>{' '}
                                                <Typography.Text className={styles.notificationMessage}>
                                                    {t('data product:')}
                                                </Typography.Text>
                                            </div>
                                            <Tag color="blue" className={styles.timestampTag}>
                                                {userNotification.notification.data_product_dataset.denied_on
                                                    ? formatDateToNow(
                                                          userNotification.notification.data_product_dataset.denied_on,
                                                      )
                                                    : undefined}
                                            </Tag>
                                            <Button
                                                type="text"
                                                size="small"
                                                style={{ padding: 0 }}
                                                onClick={() => handleRemoveNotification(userNotification.id)}
                                            >
                                                <CloseOutlined />
                                            </Button>
                                        </div>

                                        <div className={styles.notificationContent}>
                                            <Typography.Text className={styles.notificationMessage}>
                                                {t('Read access denied to dataset:')}{' '}
                                                <Link
                                                    onClick={(e) => e.stopPropagation()}
                                                    to={createDatasetIdPath(
                                                        userNotification.notification.data_product_dataset.dataset_id,
                                                    )}
                                                >
                                                    {userNotification.notification.data_product_dataset.dataset.name}
                                                </Link>
                                            </Typography.Text>
                                        </div>
                                    </div>
                                ) : (
                                    <div className={styles.notification}>
                                        <div className={styles.notificationHeader}>
                                            <div className={styles.notificationTitle}>
                                                <Link onClick={(e) => e.stopPropagation()} to={link}>
                                                    {
                                                        userNotification.notification.data_product_dataset.data_product
                                                            .name
                                                    }
                                                </Link>
                                                <Link
                                                    onClick={(e) => e.stopPropagation()}
                                                    to={createDatasetIdPath(
                                                        userNotification.notification.data_product_dataset.dataset_id,
                                                    )}
                                                >
                                                    {userNotification.notification.data_product_dataset.dataset.name}
                                                </Link>{' '}
                                                <Typography.Text className={styles.notificationMessage}>
                                                    {t('dataset:')}
                                                </Typography.Text>
                                            </div>
                                            <Tag color="blue" className={styles.timestampTag}>
                                                {userNotification.notification.data_product_dataset.denied_on
                                                    ? formatDateToNow(
                                                          userNotification.notification.data_product_dataset.denied_on,
                                                      )
                                                    : undefined}
                                            </Tag>
                                            <Button
                                                type="text"
                                                size="small"
                                                style={{ padding: 0 }}
                                                onClick={() => handleRemoveNotification(userNotification.id)}
                                            >
                                                <CloseOutlined />
                                            </Button>
                                        </div>

                                        <div className={styles.notificationContent}>
                                            <Typography.Text className={styles.notificationMessage}>
                                                {t('Read access has been denied to data product:')}{' '}
                                                <Link onClick={(e) => e.stopPropagation()} to={link}>
                                                    {
                                                        userNotification.notification.data_product_dataset.data_product
                                                            .name
                                                    }
                                                </Link>{' '}
                                            </Typography.Text>
                                        </div>
                                    </div>
                                );
                            break;
                    }
                    navigatePath = createDatasetIdPath(
                        userNotification.notification.data_product_dataset.dataset_id,
                        DatasetTabKeys.DataProduct,
                    );
                    break;

                case NotificationTypes.DataOutputDatasetNotification:
                    link = createDataOutputIdPath(
                        userNotification.notification.data_output_dataset.data_output_id,
                        userNotification.notification.data_output_dataset.data_output.owner_id,
                    );
                    switch (userNotification.notification.data_output_dataset.status) {
                        case DataOutputDatasetLinkStatus.Approved:
                            description = (
                                <div className={styles.notification}>
                                    <div className={styles.notificationHeader}>
                                        <div>
                                            <Link onClick={(e) => e.stopPropagation()} to={link}>
                                                {userNotification.notification.data_output_dataset.data_output.name}
                                            </Link>{' '}
                                            <Typography.Text className={styles.notificationMessage}>
                                                {t('data output:')}
                                            </Typography.Text>
                                        </div>
                                        <Tag color="blue" className={styles.timestampTag}>
                                            {userNotification.notification.data_output_dataset.approved_on
                                                ? formatDateToNow(
                                                      userNotification.notification.data_output_dataset.approved_on,
                                                  )
                                                : undefined}
                                        </Tag>
                                        <Button
                                            type="text"
                                            size="small"
                                            style={{ padding: 0 }}
                                            onClick={() => handleRemoveNotification(userNotification.id)}
                                        >
                                            <CloseOutlined />
                                        </Button>
                                    </div>

                                    <div className={styles.notificationContent}>
                                        <Typography.Text className={styles.notificationMessage}>
                                            {t('Linking approved for dataset:')}{' '}
                                            <Link
                                                onClick={(e) => e.stopPropagation()}
                                                to={createDatasetIdPath(
                                                    userNotification.notification.data_output_dataset.dataset_id,
                                                )}
                                            >
                                                {userNotification.notification.data_output_dataset.dataset.name}
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
                                                {userNotification.notification.data_output_dataset.data_output.name}
                                            </Link>{' '}
                                            <Typography.Text className={styles.notificationMessage}>
                                                {t('data output:')}
                                            </Typography.Text>
                                        </div>
                                        <Tag color="blue" className={styles.timestampTag}>
                                            {userNotification.notification.data_output_dataset.denied_on
                                                ? formatDateToNow(
                                                      userNotification.notification.data_output_dataset.denied_on,
                                                  )
                                                : undefined}
                                        </Tag>
                                        <Button
                                            type="text"
                                            size="small"
                                            style={{ padding: 0 }}
                                            onClick={() => handleRemoveNotification(userNotification.id)}
                                        >
                                            <CloseOutlined />
                                        </Button>
                                    </div>

                                    <div className={styles.notificationContent}>
                                        <Typography.Text className={styles.notificationMessage}>
                                            {t('Linking denied for dataset:')}{' '}
                                            <Link
                                                onClick={(e) => e.stopPropagation()}
                                                to={createDatasetIdPath(
                                                    userNotification.notification.data_output_dataset.dataset_id,
                                                )}
                                            >
                                                {userNotification.notification.data_output_dataset.dataset.name}
                                            </Link>
                                        </Typography.Text>
                                    </div>
                                </div>
                            );
                            break;
                    }
                    navigatePath = createDatasetIdPath(
                        userNotification.notification.data_output_dataset.dataset_id,
                        DatasetTabKeys.DataOutput,
                    );
                    break;

                case NotificationTypes.DataProductMembershipNotification:
                    link = createDataProductIdPath(
                        userNotification.notification.data_product_membership.data_product_id,
                    );
                    switch (userNotification.notification.data_product_membership.status) {
                        case DataProductMembershipStatus.Approved:
                            description = (
                                <div className={styles.notification}>
                                    <div className={styles.notificationHeader}>
                                        <div>
                                            <Link onClick={(e) => e.stopPropagation()} to={link}>
                                                {
                                                    userNotification.notification.data_product_membership.data_product
                                                        .name
                                                }
                                            </Link>{' '}
                                            <Typography.Text className={styles.notificationMessage}>
                                                {t('data product:')}
                                            </Typography.Text>
                                        </div>
                                        <Tag color="blue" className={styles.timestampTag}>
                                            {userNotification.notification.data_product_membership.approved_on
                                                ? formatDateToNow(
                                                      userNotification.notification.data_product_membership.approved_on,
                                                  )
                                                : undefined}
                                        </Tag>
                                        <Button
                                            type="text"
                                            size="small"
                                            style={{ padding: 0 }}
                                            onClick={() => handleRemoveNotification(userNotification.id)}
                                        >
                                            <CloseOutlined />
                                        </Button>
                                    </div>

                                    <div className={styles.notificationContent}>
                                        <Typography.Text className={styles.notificationMessage}>
                                            {t('You have been granted the role of {{role}}', {
                                                role: userNotification.notification.data_product_membership.role,
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
                                                {
                                                    userNotification.notification.data_product_membership.data_product
                                                        .name
                                                }
                                            </Link>{' '}
                                            <Typography.Text className={styles.notificationMessage}>
                                                {t('data product:')}
                                            </Typography.Text>
                                        </div>
                                        <Tag color="blue" className={styles.timestampTag}>
                                            {userNotification.notification.data_product_membership.denied_on
                                                ? formatDateToNow(
                                                      userNotification.notification.data_product_membership.denied_on,
                                                  )
                                                : undefined}
                                        </Tag>
                                        <Button
                                            type="text"
                                            size="small"
                                            style={{ padding: 0 }}
                                            onClick={() => handleRemoveNotification(userNotification.id)}
                                        >
                                            <CloseOutlined />
                                        </Button>
                                    </div>

                                    <div className={styles.notificationContent}>
                                        <Typography.Text className={styles.notificationMessage}>
                                            {t('You have been denied the role of {{role}}', {
                                                role: userNotification.notification.data_product_membership.role,
                                            })}{' '}
                                        </Typography.Text>
                                    </div>
                                </div>
                            );
                            break;
                    }
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
                label: <div className={styles.notificationItem}>{description}</div>,
                onClick: () => navigate(navigatePath),
            };
        },
        [],
    );

    const handleRedirectHome = () => {
        navigate('/');
    };

    const notificationItems = useMemo(() => {
        const notificationCreatedItems = notifications?.map((action) =>
            createItem({ ...action }, navigate, t, currentUser, handleRemoveNotification),
        );
        return notificationCreatedItems ?? [];
    }, [notifications, createItem, navigate, t, currentUser, handleRemoveNotification]);

    const notificationItemCount = useMemo(() => notificationItems?.length || 0, [notificationItems]);

    const items: MenuProps['items'] = [
        {
            type: 'group',
            label: (
                <div className={styles.notificationTitlebar}>
                    <Flex>
                        <Typography.Title level={4}>Notifications</Typography.Title>{' '}
                        <Badge count={notificationItemCount} color="gray" size="small" />
                    </Flex>
                    {pendingActionsCount != 0 && (
                        <Button type="link" value="pendingRequests" onClick={handleRedirectHome}>
                            <strong> {t('View requests')}</strong>
                            <Badge count={pendingActionsCount} color="gray" size="small" />
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
                count={notificationItemCount + pendingActionsCount}
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
