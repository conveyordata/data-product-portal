import { Badge, Col, Pagination, Row, Typography } from 'antd';
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

const ROW_GUTTER = 96;
const COL_SPAN = 12;

const createPendingItem = (userNotification: NotificationModel, t: TFunction) => {
    let link, description, navigatePath, date, author, origin;

    switch (userNotification.notification.configuration_type) {
        case NotificationTypes.DataProductDataset:
            link = createDataProductIdPath(userNotification.notification.data_product_dataset.data_product_id);
            description = (
                <Typography.Text className="description">
                    {t('Requests for read access to the')}{' '}
                    <Link
                        onClick={(e) => e.stopPropagation()}
                        to={createDatasetIdPath(userNotification.notification.data_product_dataset.dataset_id)}
                    >
                        {userNotification.notification.data_product_dataset.dataset.name}
                    </Link>{' '}
                    {t('dataset.')}
                </Typography.Text>
            );
            origin = (
                <Typography.Text>
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {userNotification.notification.data_product_dataset.data_product.name}
                    </Link>{' '}
                    {t('data product.')}{' '}
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

        case NotificationTypes.DataOutputDataset:
            link = createDataOutputIdPath(
                userNotification.notification.data_output_dataset.data_output_id,
                userNotification.notification.data_output_dataset.data_output.owner_id,
            );
            description = (
                <Typography.Text>
                    {t('Requests to create a link to the')}{' '}
                    <Link
                        onClick={(e) => e.stopPropagation()}
                        to={createDatasetIdPath(userNotification.notification.data_output_dataset.dataset_id)}
                    >
                        {userNotification.notification.data_output_dataset.dataset.name}
                    </Link>{' '}
                    {t('dataset.')}
                </Typography.Text>
            );
            origin = (
                <Typography.Text>
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

        case NotificationTypes.DataProductMembership:
            link = createDataProductIdPath(userNotification.notification.data_product_membership.data_product_id);
            description = (
                <Typography.Text>
                    {t('Requests to join the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {userNotification.notification.data_product_membership.data_product.name}
                    </Link>{' '}
                    {t('data product team.')}
                </Typography.Text>
            );
            origin = null;
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
        origin: origin,
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
        <div className={styles.requestsInbox}>
            <div className={styles.sectionTitle}>
                <Typography.Title level={3}>
                    {t('Pending Requests')}{' '}
                    <Badge count={pendingItems.length} color="gray" className={styles.requestsInfo} />
                </Typography.Title>
                <div className={styles.pagination}>
                    <Pagination
                        current={pagination.current}
                        pageSize={pagination.pageSize}
                        total={pendingItems.length}
                        onChange={onPaginationChange}
                        size="small"
                    />
                </div>
            </div>
            <div className={styles.contentSecondary}>
                <Row gutter={ROW_GUTTER}>
                    <Col span={COL_SPAN}>
                        <PendingRequestsList
                            pendingActionItems={pendingItems}
                            isFetching={isFetching}
                            pagination={pagination}
                            isFirstHalf={true}
                        />
                    </Col>
                    <Col span={COL_SPAN}>
                        <PendingRequestsList
                            pendingActionItems={pendingItems}
                            isFetching={isFetching}
                            pagination={pagination}
                            isFirstHalf={false}
                        />
                    </Col>
                </Row>
            </div>
        </div>
    );
}
