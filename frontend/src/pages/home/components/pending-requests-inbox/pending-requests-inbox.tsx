import { Badge, Flex, Form, Pagination, theme, Typography } from 'antd';
import { TFunction } from 'i18next';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link } from 'react-router';

import { Searchbar } from '@/components/form';
import { useListPagination } from '@/hooks/use-list-pagination';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useGetPendingActionNotificationsQuery } from '@/store/features/notifications/notifications-api-slice';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import { NotificationModel, NotificationTypes } from '@/types/notifications/notification.contract';

import styles from './pending-requests-inbox.module.scss';
import { PendingRequestsList } from './pending-requests-list';

const createPendingItem = (userNotification: NotificationModel, t: TFunction, colors: string[]) => {
    let link, description, navigatePath, date, author, initials, message, color;

    function getInitials(firstName: string, lastName: string) {
        return (firstName?.charAt(0) || '') + (lastName ? lastName.charAt(0) : '');
    }

    switch (userNotification.notification.configuration_type) {
        case NotificationTypes.DataProductDatasetNotification:
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
                    {t('Accepting will grant read access to the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {userNotification.notification.reference.data_product.name}
                    </Link>{' '}
                    {t('data product.')}{' '}
                </Typography.Text>
            );
            color = colors[0];
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
            link = createDataOutputIdPath(
                userNotification.notification.reference.data_output_id,
                userNotification.notification.reference.data_output.owner_id,
            );
            description = (
                <Typography.Text>
                    {t('Requests to create a link with the')}{' '}
                    <Link
                        onClick={(e) => e.stopPropagation()}
                        to={createDatasetIdPath(userNotification.notification.reference.dataset_id)}
                    >
                        {userNotification.notification.reference.dataset.name}
                    </Link>{' '}
                    {t('dataset')}
                </Typography.Text>
            );
            message = (
                <Typography.Text>
                    {t('Requests to create a link with the')}{' '}
                    <Link
                        onClick={(e) => e.stopPropagation()}
                        to={createDatasetIdPath(userNotification.notification.reference.dataset_id)}
                    >
                        {userNotification.notification.reference.dataset.name}
                    </Link>{' '}
                    {t('dataset, from the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {userNotification.notification.reference.data_output.name}
                    </Link>{' '}
                    {t('data output.')}
                </Typography.Text>
            );
            color = colors[1];
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
            link = createDataProductIdPath(userNotification.notification.reference.data_product_id);
            description = (
                <Typography.Text>
                    {t('Requests to join the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {userNotification.notification.reference.data_product.name}
                    </Link>{' '}
                    {t('data product team.')}
                </Typography.Text>
            );
            message = (
                <Typography.Text>
                    {t('Requests to join the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {userNotification.notification.reference.data_product.name}
                    </Link>{' '}
                    {t('data product team.')}
                </Typography.Text>
            );
            color = colors[2];
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
    };
};

export function PendingRequestsInbox() {
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser);
    const [searchForm] = Form.useForm();
    const {
        token: { colorSuccess, colorWarning, colorError },
    } = theme.useToken();

    const { data: pendingActions, isFetching } = useGetPendingActionNotificationsQuery();

    const colors = [colorSuccess, colorWarning, colorError];

    const pendingItems = useMemo(() => {
        const userNotifications = pendingActions?.map((userNotification) =>
            createPendingItem({ ...userNotification }, t, colors),
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

    if (pendingItems.length == 0 && isFetching == false) {
        return (
            <Flex className={styles.backgroundImage}>
                <Typography.Title level={2}>
                    {t('Welcome back, {{name}}', { name: currentUser?.first_name })}
                </Typography.Title>
                <div className={styles.searchBar}>
                    <Searchbar form={searchForm} placeholder={t('Search for data products and datasets by name')} />
                </div>
            </Flex>
        );
    }

    return (
        <div className={styles.requestsInbox}>
            <div className={styles.sectionTitle}>
                <Typography.Title level={3}>
                    {t('Pending Requests')}
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
                <PendingRequestsList
                    pendingActionItems={pendingItems}
                    isFetching={isFetching}
                    pagination={pagination}
                />
            </div>
        </div>
    );
}
