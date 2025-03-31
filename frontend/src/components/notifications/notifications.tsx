import { BellOutlined, ExportOutlined } from '@ant-design/icons';
import { Badge, Button, Dropdown, Flex, type MenuProps, Space, Tag, theme, Typography } from 'antd';
import type { TFunction } from 'i18next';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, type NavigateFunction, useNavigate } from 'react-router';

import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { useGetNotificationsQuery } from '@/store/features/notifications/notifications-api-slice';
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

    const createItem = useCallback((userNotification: NotificationModel, navigate: NavigateFunction, t: TFunction) => {
        let link, description, navigatePath;

        switch (userNotification.notification.configuration_type) {
            case NotificationTypes.DataProductDataset:
                link = createDataProductIdPath(userNotification.notification.data_product_dataset.data_product_id);
                switch (userNotification.notification.data_product_dataset.status) {
                    case DataProductDatasetLinkStatus.Approved:
                        description = (
                            <div className={styles.notification}>
                                <div className={styles.notificationHeader}>
                                    <div>
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_product_dataset.data_product.name}
                                        </Link>{' '}
                                        <Typography.Text className={styles.notificationMessage}>
                                            {t('data product:')}
                                        </Typography.Text>
                                    </div>

                                    <Tag color="blue" className={styles.timestampTag}>
                                        {t('{{time}}', {
                                            time: userNotification.notification.data_product_dataset.approved_on
                                                ? formatDateToNow(
                                                      userNotification.notification.data_product_dataset.approved_on,
                                                  )
                                                : undefined,
                                        })}
                                    </Tag>
                                    <ExportOutlined />
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
                        );
                        break;
                    case DataProductDatasetLinkStatus.Denied:
                        description = (
                            <div className={styles.notification}>
                                <div className={styles.notificationHeader}>
                                    <div>
                                        <Link onClick={(e) => e.stopPropagation()} to={link}>
                                            {userNotification.notification.data_product_dataset.data_product.name}
                                        </Link>{' '}
                                        <Typography.Text className={styles.notificationMessage}>
                                            {t('data product:')}
                                        </Typography.Text>
                                    </div>

                                    <Tag color="blue" className={styles.timestampTag}>
                                        {t('{{time}}', {
                                            time: userNotification.notification.data_product_dataset.approved_on
                                                ? formatDateToNow(
                                                      userNotification.notification.data_product_dataset.approved_on,
                                                  )
                                                : undefined,
                                        })}
                                    </Tag>
                                    <ExportOutlined />
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
                        );
                        break;
                }
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
                                        {t('{{time}}', {
                                            time: userNotification.notification.data_output_dataset.approved_on
                                                ? formatDateToNow(
                                                      userNotification.notification.data_output_dataset.approved_on,
                                                  )
                                                : undefined,
                                        })}
                                    </Tag>
                                    <ExportOutlined />
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
                                        {t('{{time}}', {
                                            time: userNotification.notification.data_output_dataset.approved_on
                                                ? formatDateToNow(
                                                      userNotification.notification.data_output_dataset.approved_on,
                                                  )
                                                : undefined,
                                        })}
                                    </Tag>
                                    <ExportOutlined />
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

            case NotificationTypes.DataProductMembership:
                link = createDataProductIdPath(userNotification.notification.data_product_membership.data_product_id);
                switch (userNotification.notification.data_product_membership.status) {
                    case DataProductMembershipStatus.Approved:
                        description = (
                            <Typography.Text>
                                {t('{{name}} approved your request to join the data product', {
                                    name: userNotification.notification.data_product_membership.approved_by?.first_name,
                                })}{' '}
                                <Link onClick={(e) => e.stopPropagation()} to={link}>
                                    {userNotification.notification.data_product_membership.data_product.name}
                                </Link>{' '}
                                {t('team')}{' '}
                            </Typography.Text>
                        );
                        break;
                    case DataProductMembershipStatus.Denied:
                        description = (
                            <Typography.Text>
                                {t('{{name}} denied your request to join the data product', {
                                    name: userNotification.notification.data_product_membership.denied_by?.first_name,
                                })}{' '}
                                <Link onClick={(e) => e.stopPropagation()} to={link}>
                                    {userNotification.notification.data_product_membership.data_product.name}
                                </Link>{' '}
                                {t('team')}{' '}
                            </Typography.Text>
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
    }, []);

    const notificationItems = useMemo(() => {
        const notificationCreatedItems = notifications?.map((action) => createItem({ ...action }, navigate, t));
        return notificationCreatedItems ?? [];
    }, [notifications, createItem, navigate, t]);

    const items: MenuProps['items'] = [
        {
            type: 'group',
            label: notificationItems?.length > 0 ? null : t('No notifications available'),
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
