import { CheckCircleOutlined } from '@ant-design/icons';
import { Badge, Col, Empty, Flex, Pagination, theme, Typography } from 'antd';
import { TFunction } from 'i18next';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import { useListPagination } from '@/hooks/use-list-pagination';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { useGetPendingActionNotificationsQuery } from '@/store/features/notifications/notifications-api-slice';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import { NotificationModel, NotificationTypes } from '@/types/notifications/notification.contract';

import styles from './pending-requests-inbox.module.scss';
import { PendingRequestsList } from './pending-requests-list';
import { SelectableTab } from './pending-requests-menu-tab';

const createPendingItem = (
    userNotification: NotificationModel,
    t: TFunction,
    colors: { [key in NotificationTypes]: string },
) => {
    let link, description, navigatePath, date, author, initials, message, color, origin, type;

    function getInitials(firstName: string, lastName: string) {
        return (firstName?.charAt(0) || '') + (lastName ? lastName.charAt(0) : '');
    }

    switch (userNotification.notification.configuration_type) {
        case NotificationTypes.DataProductDatasetNotification:
            type = NotificationTypes.DataProductDatasetNotification;
            link = createDataProductIdPath(userNotification.notification.reference.data_product_id);
            description = (
                <Typography.Text>
                    {t('requests')} <strong className={styles.descriptionCore}>{t('read access')}</strong>{' '}
                    {t('to the dataset:')}{' '}
                    <Link
                        onClick={(e) => e.stopPropagation()}
                        to={createDatasetIdPath(userNotification.notification.reference.dataset_id)}
                    >
                        <strong>{userNotification.notification.reference.dataset.name}</strong>
                    </Link>
                </Typography.Text>
            );
            message = (
                <Typography.Text>
                    {t('Accepting will grant access to the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {userNotification.notification.reference.data_product.name}
                    </Link>{' '}
                    {t('data product.')}{' '}
                </Typography.Text>
            );
            color = colors[NotificationTypes.DataProductDatasetNotification];
            origin = (
                <Typography.Text
                    style={{
                        color: color,
                    }}
                    strong
                >
                    {t('Data Product')}
                </Typography.Text>
            );
            navigatePath = createDatasetIdPath(
                userNotification.notification.reference.dataset_id,
                DatasetTabKeys.DataProduct,
            );
            date = userNotification.notification.reference.requested_on;
            author =
                userNotification.notification.reference.requested_by.first_name +
                ' ' +
                userNotification.notification.reference.requested_by.last_name;
            initials = getInitials(
                userNotification.notification.reference.requested_by.first_name,
                userNotification.notification.reference.requested_by.last_name,
            );
            break;

        case NotificationTypes.DataOutputDatasetNotification:
            type = NotificationTypes.DataOutputDatasetNotification;
            link = createDataOutputIdPath(
                userNotification.notification.reference.data_output_id,
                userNotification.notification.reference.data_output.owner_id,
            );
            description = (
                <Typography.Text>
                    {t('requests')} <strong className={styles.descriptionCore}>{t('creation of a link')}</strong>{' '}
                    {t('towards the dataset:')}{' '}
                    <Link
                        onClick={(e) => e.stopPropagation()}
                        to={createDatasetIdPath(userNotification.notification.reference.dataset_id)}
                    >
                        <strong>{userNotification.notification.reference.dataset.name}</strong>
                    </Link>{' '}
                </Typography.Text>
            );
            message = (
                <Typography.Text>
                    {t('Accepting will create a link to the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {userNotification.notification.reference.data_output.name}
                    </Link>{' '}
                    {t('data output.')}
                </Typography.Text>
            );
            color = colors[NotificationTypes.DataOutputDatasetNotification];
            origin = (
                <Typography.Text
                    style={{
                        color: color,
                    }}
                    strong
                >
                    {t('Data Output')}
                </Typography.Text>
            );
            navigatePath = createDatasetIdPath(
                userNotification.notification.reference.dataset_id,
                DatasetTabKeys.DataOutput,
            );
            date = userNotification.notification.reference.requested_on;
            author =
                userNotification.notification.reference.requested_by.first_name +
                ' ' +
                userNotification.notification.reference.requested_by.last_name;
            initials = getInitials(
                userNotification.notification.reference.requested_by.first_name,
                userNotification.notification.reference.requested_by.last_name,
            );
            break;

        case NotificationTypes.DataProductMembershipNotification:
            type = NotificationTypes.DataProductMembershipNotification;
            link = createDataProductIdPath(userNotification.notification.reference.data_product_id);
            description = (
                <Typography.Text>
                    {t('requests to ')} <strong className={styles.descriptionCore}>{t('join the team')}</strong>{' '}
                    {t('of the data product:')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        <strong>{userNotification.notification.reference.data_product.name}</strong>
                    </Link>
                </Typography.Text>
            );
            message = (
                <Typography.Text>
                    {t('Accepting will grant the role of {{role}} to {{firstName}} {{lastName}}.', {
                        role: userNotification.notification.reference.role,
                        firstName: userNotification.notification.reference.user.first_name,
                        lastName: userNotification.notification.reference.user.last_name,
                    })}
                </Typography.Text>
            );
            color = colors[NotificationTypes.DataProductMembershipNotification];
            origin = (
                <Typography.Text
                    style={{
                        color: color,
                    }}
                    strong
                >
                    {t('Person')}
                </Typography.Text>
            );
            navigatePath = createDataProductIdPath(
                userNotification.notification.reference.data_product_id,
                DataProductTabKeys.Team,
            );
            date = userNotification.notification.reference.requested_on;
            author =
                userNotification.notification.reference.user.first_name +
                ' ' +
                userNotification.notification.reference.user.last_name;
            initials = getInitials(
                userNotification.notification.reference.user.first_name,
                userNotification.notification.reference.user.last_name,
            );
            break;

        default:
            return null;
    }

    return {
        key: userNotification.id,
        description: description,
        navigatePath: navigatePath,
        date: date,
        author: author,
        initials: initials,
        message: message,
        color: color,
        origin: origin,
        type: type,
    };
};

export function PendingRequestsInbox() {
    const { t } = useTranslation();
    const {
        token: { colorSuccess, colorWarning, colorError },
    } = theme.useToken();
    const [selectedTypes, setSelectedTypes] = useState<Set<NotificationTypes>>(new Set());

    const { data: pendingActions, isFetching } = useGetPendingActionNotificationsQuery();

    const pendingItems = useMemo(() => {
        const colors = {
            [NotificationTypes.DataProductDatasetNotification]: colorWarning,
            [NotificationTypes.DataOutputDatasetNotification]: colorError,
            [NotificationTypes.DataProductMembershipNotification]: colorSuccess,
        };

        const userNotifications = pendingActions?.map((userNotification) =>
            createPendingItem({ ...userNotification }, t, colors),
        );
        if (!userNotifications) {
            return [];
        }
        return userNotifications.filter((item) => item !== null);
    }, [pendingActions, t, colorError, colorSuccess, colorWarning]);

    const { pagination, handlePaginationChange, resetPagination, handleTotalChange } = useListPagination({});

    const onPaginationChange = (current: number, pageSize: number) => {
        handlePaginationChange({ current, pageSize });
    };

    const handleTabChange = (type: NotificationTypes, selected: boolean) => {
        resetPagination();
        setSelectedTypes((prev) => {
            const newSet = new Set(prev);
            if (selected) {
                newSet.add(type);
            } else {
                newSet.delete(type);
            }
            return newSet;
        });
    };

    const itemCountByType = useMemo(() => {
        const counts: { [key in NotificationTypes]: number } = {
            [NotificationTypes.DataProductDatasetNotification]: 0,
            [NotificationTypes.DataOutputDatasetNotification]: 0,
            [NotificationTypes.DataProductMembershipNotification]: 0,
        };

        pendingItems.forEach((item) => {
            if (item) {
                counts[item.type]++;
            }
        });

        return counts;
    }, [pendingItems]);

    const slicedPendingActionItems = useMemo(() => {
        return (
            selectedTypes.size === 0 ? pendingItems : pendingItems.filter((item) => selectedTypes.has(item.type))
        ).sort((a, b) => {
            if (!a?.date || !b?.date) {
                return 0;
            }
            return new Date(a.date).getTime() - new Date(b.date).getTime();
        });
    }, [pendingItems, selectedTypes]);

    useEffect(() => {
        handleTotalChange(slicedPendingActionItems.length);
    }, [slicedPendingActionItems.length, handleTotalChange]);

    if (pendingItems.length == 0 && isFetching == false) {
        return (
            <div className={styles.requestsInbox}>
                <Typography.Title level={1} className={styles.welcomeContent}>
                    {t('Welcome back')}
                </Typography.Title>
                <Empty
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                    description={
                        <Typography.Text>
                            <CheckCircleOutlined /> {t(`You have no requests to handle.`)}
                        </Typography.Text>
                    }
                ></Empty>
            </div>
        );
    }

    return (
        <div className={styles.requestsInbox}>
            <div className={styles.sectionTitle}>
                <Col span={12}>
                    <Typography.Title level={3}>
                        {t('Pending Requests')}
                        <Badge count={pendingItems.length} color="gray" className={styles.requestsInfo} />
                    </Typography.Title>
                </Col>
                <Col span={12} className={styles.topRightColumn}>
                    <Flex className={styles.filterBar} gap={0}>
                        <SelectableTab
                            type={NotificationTypes.DataProductMembershipNotification}
                            title="Team Request"
                            requestsCount={itemCountByType[NotificationTypes.DataProductMembershipNotification]}
                            color={colorSuccess}
                            onSelectChange={handleTabChange}
                        />
                        <SelectableTab
                            type={NotificationTypes.DataOutputDatasetNotification}
                            title="Data Output"
                            requestsCount={itemCountByType[NotificationTypes.DataOutputDatasetNotification]}
                            color={colorError}
                            onSelectChange={handleTabChange}
                        />
                        <SelectableTab
                            type={NotificationTypes.DataProductDatasetNotification}
                            title="Data Product"
                            requestsCount={itemCountByType[NotificationTypes.DataProductDatasetNotification]}
                            color={colorWarning}
                            onSelectChange={handleTabChange}
                        />
                    </Flex>

                    <div className={styles.pagination}>
                        <Pagination
                            current={pagination.current}
                            pageSize={pagination.pageSize}
                            total={slicedPendingActionItems.length}
                            onChange={onPaginationChange}
                            size="small"
                        />
                    </div>
                </Col>
            </div>

            <div className={styles.contentSecondary}>
                <PendingRequestsList
                    pendingActionItems={slicedPendingActionItems}
                    isFetching={isFetching}
                    pagination={pagination}
                />
            </div>
        </div>
    );
}
