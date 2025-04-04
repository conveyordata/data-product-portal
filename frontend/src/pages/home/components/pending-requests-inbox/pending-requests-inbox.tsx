import { Badge, Col, Flex, Form, Pagination, theme, Typography } from 'antd';
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
import { SelectableTab } from './pending-requests-menu-tab';

const createPendingItem = (
    userNotification: NotificationModel,
    t: TFunction,
    colors: { [key in NotificationTypes]: string },
) => {
    let link, description, navigatePath, date, author, initials, message, color, origin;

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

    const pendingItems = useMemo(() => {
        const colors = {
            [NotificationTypes.DataProductDatasetNotification]: colorSuccess,
            [NotificationTypes.DataOutputDatasetNotification]: colorWarning,
            [NotificationTypes.DataProductMembershipNotification]: colorError,
        };

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
    }, [pendingActions, t, colorError, colorSuccess, colorWarning]);

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
                <Col span={12}>
                    <Typography.Title level={3}>
                        {t('Pending Requests')}
                        <Badge count={pendingItems.length} color="gray" className={styles.requestsInfo} />
                    </Typography.Title>
                </Col>
                <Col span={12} className={styles.topRightColumn}>
                    <SelectableTab title="Team Requests" requestsCount={9} color={colorSuccess} />
                    <SelectableTab title="Data Output" requestsCount={1} color={colorWarning} />
                    <SelectableTab title="Data Products" requestsCount={4} color={colorError} />
                    <div className={styles.pagination}>
                        <Pagination
                            current={pagination.current}
                            pageSize={pagination.pageSize}
                            total={pendingItems.length}
                            onChange={onPaginationChange}
                            size="small"
                        />
                    </div>
                </Col>
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
