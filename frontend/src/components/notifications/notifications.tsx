import { BellOutlined, ExportOutlined } from '@ant-design/icons';
import { Badge, Button, Dropdown, Flex, type MenuProps, Space, theme, Typography } from 'antd';
import type { TFunction } from 'i18next';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link, type NavigateFunction, useNavigate } from 'react-router';

import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useGetNotificationsQuery } from '@/store/features/notifications/notifications-api-slice';
import { DataOutputDatasetLinkStatus } from '@/types/data-output-dataset';
import { DataProductDatasetLinkStatus } from '@/types/data-product-dataset';
import { DataProductMembershipStatus } from '@/types/data-product-membership';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import { NotificationModel, NotificationTypes } from '@/types/notifications/notification.contract';
import { UserContract } from '@/types/users';

import styles from './notifications.module.scss';

export function Notifications() {
    const {
        token: { colorPrimary },
    } = theme.useToken();
    const { t } = useTranslation();
    const navigate = useNavigate();
    const currentUser = useSelector(selectCurrentUser);

    const { data: notifications } = useGetNotificationsQuery();

    const createItem = useCallback(
        (
            userNotification: NotificationModel,
            navigate: NavigateFunction,
            t: TFunction,
            currentUser: UserContract | null,
        ) => {
            let link, description, navigatePath, received;

            switch (userNotification.notification.notification_type) {
                case NotificationTypes.DataProductDatasetNotification:
                    link = createDataProductIdPath(userNotification.notification.data_product_dataset.data_product_id);
                    switch (userNotification.notification.notification_origin) {
                        case DataProductDatasetLinkStatus.Approved:
                            description =
                                currentUser?.id ===
                                userNotification.notification.data_product_dataset.requested_by.id ? (
                                    <Typography.Text>
                                        {t('{{name}} approved your request made on behalf of data output', {
                                            name: userNotification.notification.data_product_dataset.approved_by
                                                ?.first_name,
                                        })}{' '}
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_product_dataset.data_product.name}
                                        </Link>{' '}
                                        {t('for read access to the dataset')}{' '}
                                        <Link
                                            onClick={(e) => e.stopPropagation()}
                                            to={createDatasetIdPath(
                                                userNotification.notification.data_product_dataset.dataset_id,
                                            )}
                                        >
                                            {userNotification.notification.data_product_dataset.dataset.name}
                                        </Link>
                                    </Typography.Text>
                                ) : (
                                    <Typography.Text>
                                        {t('The data output', {
                                            name: userNotification.notification.data_product_dataset.approved_by
                                                ?.first_name,
                                        })}{' '}
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_product_dataset.data_product.name}
                                        </Link>{' '}
                                        {t('has been granted read access to the dataset')}{' '}
                                        <Link
                                            onClick={(e) => e.stopPropagation()}
                                            to={createDatasetIdPath(
                                                userNotification.notification.data_product_dataset.dataset_id,
                                            )}
                                        >
                                            {userNotification.notification.data_product_dataset.dataset.name}
                                        </Link>
                                    </Typography.Text>
                                );
                            received = userNotification.notification.data_product_dataset.approved_on;
                            break;
                        case DataProductDatasetLinkStatus.Denied:
                            description =
                                currentUser?.id ===
                                userNotification.notification.data_product_dataset.requested_by.id ? (
                                    <Typography.Text>
                                        {t('{{name}} denied your request made on behalf of data output', {
                                            name: userNotification.notification.data_product_dataset.denied_by
                                                ?.first_name,
                                        })}{' '}
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_product_dataset.data_product.name}
                                        </Link>{' '}
                                        {t('for read access to the dataset')}{' '}
                                        <Link
                                            onClick={(e) => e.stopPropagation()}
                                            to={createDatasetIdPath(
                                                userNotification.notification.data_product_dataset.dataset_id,
                                            )}
                                        >
                                            {userNotification.notification.data_product_dataset.dataset.name}
                                        </Link>
                                    </Typography.Text>
                                ) : (
                                    <Typography.Text>
                                        {t('The data output', {
                                            name: userNotification.notification.data_product_dataset.denied_by
                                                ?.first_name,
                                        })}{' '}
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_product_dataset.data_product.name}
                                        </Link>{' '}
                                        {t('has been denied read access to the dataset')}{' '}
                                        <Link
                                            onClick={(e) => e.stopPropagation()}
                                            to={createDatasetIdPath(
                                                userNotification.notification.data_product_dataset.dataset_id,
                                            )}
                                        >
                                            {userNotification.notification.data_product_dataset.dataset.name}
                                        </Link>
                                    </Typography.Text>
                                );
                            received = userNotification.notification.data_product_dataset.denied_on;
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
                    switch (userNotification.notification.notification_origin) {
                        case DataOutputDatasetLinkStatus.Approved:
                            description =
                                currentUser?.id ===
                                userNotification.notification.data_output_dataset.requested_by.id ? (
                                    <Typography.Text>
                                        {t('{{name}} approved your request made on behalf of data output', {
                                            name: userNotification.notification.data_output_dataset.approved_by
                                                ?.first_name,
                                        })}{' '}
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_output_dataset.data_output.name}
                                        </Link>{' '}
                                        {t('for a link to the dataset')}{' '}
                                        <Link
                                            onClick={(e) => e.stopPropagation()}
                                            to={createDatasetIdPath(
                                                userNotification.notification.data_output_dataset.dataset_id,
                                            )}
                                        >
                                            {userNotification.notification.data_output_dataset.dataset.name}
                                        </Link>
                                    </Typography.Text>
                                ) : (
                                    <Typography.Text>
                                        {t('The data output', {
                                            name: userNotification.notification.data_output_dataset.approved_by
                                                ?.first_name,
                                        })}{' '}
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_output_dataset.data_output.name}
                                        </Link>{' '}
                                        {t('has been granted a link to the dataset')}{' '}
                                        <Link
                                            onClick={(e) => e.stopPropagation()}
                                            to={createDatasetIdPath(
                                                userNotification.notification.data_output_dataset.dataset_id,
                                            )}
                                        >
                                            {userNotification.notification.data_output_dataset.dataset.name}
                                        </Link>
                                    </Typography.Text>
                                );
                            received = userNotification.notification.data_output_dataset.approved_on;
                            break;
                        case DataOutputDatasetLinkStatus.Denied:
                            description =
                                currentUser?.id ===
                                userNotification.notification.data_output_dataset.requested_by.id ? (
                                    <Typography.Text>
                                        {t('{{name}} denied your request made on behalf of data output', {
                                            name: userNotification.notification.data_output_dataset.denied_by
                                                ?.first_name,
                                        })}{' '}
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_output_dataset.data_output.name}
                                        </Link>{' '}
                                        {t('for a link to the dataset')}{' '}
                                        <Link
                                            onClick={(e) => e.stopPropagation()}
                                            to={createDatasetIdPath(
                                                userNotification.notification.data_output_dataset.dataset_id,
                                            )}
                                        >
                                            {userNotification.notification.data_output_dataset.dataset.name}
                                        </Link>
                                    </Typography.Text>
                                ) : (
                                    <Typography.Text>
                                        {t('The data output', {
                                            name: userNotification.notification.data_output_dataset.approved_by
                                                ?.first_name,
                                        })}{' '}
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_output_dataset.data_output.name}
                                        </Link>{' '}
                                        {t('has been denied a link to the dataset')}{' '}
                                        <Link
                                            onClick={(e) => e.stopPropagation()}
                                            to={createDatasetIdPath(
                                                userNotification.notification.data_output_dataset.dataset_id,
                                            )}
                                        >
                                            {userNotification.notification.data_output_dataset.dataset.name}
                                        </Link>
                                    </Typography.Text>
                                );
                            received = userNotification.notification.data_output_dataset.denied_on;
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
                    switch (userNotification.notification.notification_origin) {
                        case DataProductMembershipStatus.Approved:
                            description =
                                currentUser?.id === userNotification.notification.data_product_membership.user.id ? (
                                    <Typography.Text>
                                        {t('{{name}} approved your request to join the data product', {
                                            name: userNotification.notification.data_product_membership.approved_by
                                                ?.first_name,
                                        })}{' '}
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_product_membership.data_product.name}
                                        </Link>{' '}
                                        {t('team')}{' '}
                                    </Typography.Text>
                                ) : (
                                    <Typography.Text>
                                        {t(
                                            '{{name}} has been granted the role of {{role}} in the team of the data product',
                                            {
                                                name: userNotification.notification.data_product_membership.user
                                                    ?.first_name,
                                                role: userNotification.notification.data_product_membership.role,
                                            },
                                        )}{' '}
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_product_membership.data_product.name}
                                        </Link>
                                    </Typography.Text>
                                );
                            received = userNotification.notification.data_product_membership.approved_on;
                            break;
                        case DataProductMembershipStatus.Denied:
                            description =
                                currentUser?.id === userNotification.notification.data_product_membership.user.id ? (
                                    <Typography.Text>
                                        {t('{{name}} denied your request to join the data product', {
                                            name: userNotification.notification.data_product_membership.denied_by
                                                ?.first_name,
                                        })}{' '}
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_product_membership.data_product.name}
                                        </Link>{' '}
                                        {t('team')}{' '}
                                    </Typography.Text>
                                ) : (
                                    <Typography.Text>
                                        {t(
                                            '{{name}} has been denied the role of {{role}} in the team of the data product',
                                            {
                                                name: userNotification.notification.data_product_membership.user
                                                    ?.first_name,
                                                role: userNotification.notification.data_product_membership.role,
                                            },
                                        )}{' '}
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_product_membership.data_product.name}
                                        </Link>
                                    </Typography.Text>
                                );
                            received = userNotification.notification.data_product_membership.denied_on;
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
                label: <Flex>{description}</Flex>,
                extra: <ExportOutlined />,
                onClick: () => navigate(navigatePath),
                received: received,
            };
        },
        [],
    );

    const notificationItems = useMemo(() => {
        const notificationCreatedItems = notifications?.map((action) =>
            createItem({ ...action }, navigate, t, currentUser),
        );
        return notificationCreatedItems ?? [];
    }, [notifications, createItem, navigate, t, currentUser]);

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
