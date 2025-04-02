import { Badge, Pagination, Typography } from 'antd';
import { TFunction } from 'i18next';
import { useMemo } from 'react';
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

const createPendingItem = (userNotification: NotificationModel, t: TFunction) => {
    let link, description, navigatePath, date, author;

    switch (userNotification.notification.configuration_type) {
        case NotificationTypes.DataProductDatasetNotification:
            link = createDataProductIdPath(userNotification.notification.data_product_dataset.data_product_id);
            description = (
                <Typography.Text>
                    {t('Made a request for read access to the')}{' '}
                    <Link
                        onClick={(e) => e.stopPropagation()}
                        to={createDatasetIdPath(userNotification.notification.data_product_dataset.dataset_id)}
                    >
                        {userNotification.notification.data_product_dataset.dataset.name}
                    </Link>{' '}
                    {t('dataset, on behalf of the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {userNotification.notification.data_product_dataset.data_product.name}
                    </Link>{' '}
                    {t('data product.')}
                </Typography.Text>
            );
            navigatePath = createDatasetIdPath(
                userNotification.notification.data_product_dataset.dataset_id,
                DatasetTabKeys.DataProduct,
            );
            date = userNotification.notification.data_product_dataset.requested_on;
            author =
                userNotification.notification.data_product_dataset.requested_by.first_name +
                ' ' +
                userNotification.notification.data_product_dataset.requested_by.last_name;
            break;

        case NotificationTypes.DataOutputDatasetNotification:
            link = createDataOutputIdPath(
                userNotification.notification.data_output_dataset.data_output_id,
                userNotification.notification.data_output_dataset.data_output.owner_id,
            );
            description = (
                <Typography.Text>
                    {t('Made a request for a link to the')}{' '}
                    <Link
                        onClick={(e) => e.stopPropagation()}
                        to={createDatasetIdPath(userNotification.notification.data_output_dataset.dataset_id)}
                    >
                        {userNotification.notification.data_output_dataset.dataset.name}
                    </Link>{' '}
                    {t('dataset, on behalf of the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {userNotification.notification.data_output_dataset.data_output.name}
                    </Link>{' '}
                    {t('data output.')}
                </Typography.Text>
            );
            navigatePath = createDatasetIdPath(
                userNotification.notification.data_output_dataset.dataset_id,
                DatasetTabKeys.DataOutput,
            );
            date = userNotification.notification.data_output_dataset.requested_on;
            author =
                userNotification.notification.data_output_dataset.requested_by.first_name +
                ' ' +
                userNotification.notification.data_output_dataset.requested_by.last_name;
            break;

        case NotificationTypes.DataProductMembershipNotification:
            link = createDataProductIdPath(userNotification.notification.data_product_membership.data_product_id);
            description = (
                <Typography.Text>
                    {t('Made a request to join the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {userNotification.notification.data_product_membership.data_product.name}
                    </Link>{' '}
                    {t('data product team.')}
                </Typography.Text>
            );
            navigatePath = createDataProductIdPath(
                userNotification.notification.data_product_membership.data_product_id,
                DataProductTabKeys.Team,
            );
            date = userNotification.notification.data_product_membership.requested_on;
            author =
                userNotification.notification.data_product_membership.user.first_name +
                ' ' +
                userNotification.notification.data_product_membership.user.last_name;
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
    };
};

export function PendingRequestsInbox() {
    const { t } = useTranslation();

    const { data: pendingActions, isFetching } = useGetPendingActionNotificationsQuery();

    const pendingItems = useMemo(() => {
        const userNotifications = pendingActions?.map((userNotification) =>
            createPendingItem({ ...userNotification }, t),
        );
        if (!userNotifications) {
            return [];
        }
        return userNotifications
            .filter((item) => item !== null)
            .sort((a, b) => {
                if (!a?.date || !b?.date) {
                    return 0;
                }
                return new Date(a.date).getTime() - new Date(b.date).getTime();
            });
    }, [pendingActions, t]);

    const { pagination, handlePaginationChange } = useListPagination({});

    const onPaginationChange = (current: number, pageSize: number) => {
        handlePaginationChange({ current, pageSize });
    };

    return (
        <div className={styles.section}>
            <div className={styles.sectionTitle}>
                <Typography.Title level={3}>
                    {t('Pending Requests')}{' '}
                    <Badge count={pendingItems.length} color="gray" className={styles.requestsInfo} />
                </Typography.Title>
                <Pagination
                    current={pagination.current}
                    pageSize={pagination.pageSize}
                    total={pendingItems.length}
                    onChange={onPaginationChange}
                    size="small"
                />
            </div>
            <div className={styles.requestsListContainer}>
                <PendingRequestsList
                    pendingActionItems={pendingItems}
                    isFetching={isFetching}
                    pagination={pagination}
                />
            </div>
        </div>
    );
}
