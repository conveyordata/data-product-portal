import { CheckCircleOutlined } from '@ant-design/icons';
import { Badge, Col, Empty, Flex, Pagination, theme, Typography } from 'antd';
import { TFunction } from 'i18next';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import { useListPagination } from '@/hooks/use-list-pagination';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import {
    useApproveDataOutputLinkMutation,
    useRejectDataOutputLinkMutation,
} from '@/store/features/data-outputs-datasets/data-outputs-datasets-api-slice';
import {
    useDenyMembershipAccessMutation,
    useGrantMembershipAccessMutation,
} from '@/store/features/data-product-memberships/data-product-memberships-api-slice';
import {
    useApproveDataProductLinkMutation,
    useRejectDataProductLinkMutation,
} from '@/store/features/data-products-datasets/data-products-datasets-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback';
import { useGetPendingActionNotificationsQuery } from '@/store/features/notifications/notifications-api-slice';
import { DataOutputDatasetLinkRequest } from '@/types/data-output-dataset';
import { DataProductDatasetLinkRequest } from '@/types/data-product-dataset';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import {
    ActionResolveRequest,
    NotificationModel,
    NotificationTypes,
} from '@/types/notifications/notification.contract';

import styles from './pending-requests-inbox.module.scss';
import { PendingRequestsList } from './pending-requests-list';
import { SelectableTab } from './pending-requests-menu-tab';

const createPendingItem = (
    userNotification: NotificationModel,
    t: TFunction,
    colors: { [key in NotificationTypes]: string },
) => {
    let link, description, navigatePath, date, author, initials, message, color, origin, type, request;

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
            request = {
                type: NotificationTypes.DataProductDatasetNotification as NotificationTypes.DataProductDatasetNotification,
                request: {
                    id: userNotification.notification.reference.id,
                    data_product_id: userNotification.notification.reference.data_product_id,
                    dataset_id: userNotification.notification.reference.dataset_id,
                },
            };
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
            request = {
                type: NotificationTypes.DataOutputDatasetNotification as NotificationTypes.DataOutputDatasetNotification,
                request: {
                    id: userNotification.notification.reference.id,
                    data_output_id: userNotification.notification.reference.data_output_id,
                    dataset_id: userNotification.notification.reference.dataset_id,
                },
            };
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
            request = {
                type: NotificationTypes.DataProductMembershipNotification as NotificationTypes.DataProductMembershipNotification,
                request: userNotification.notification.reference.id,
            };
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
        request: request,
    };
};

export function PendingRequestsInbox() {
    const { t } = useTranslation();
    const {
        token: { colorWarning, colorInfo, colorError },
    } = theme.useToken();
    const [selectedTypes, setSelectedTypes] = useState<Set<NotificationTypes>>(new Set());

    const { data: pendingActions, isFetching } = useGetPendingActionNotificationsQuery();

    const [approveDataProductLink] = useApproveDataProductLinkMutation();
    const [rejectDataProductLink] = useRejectDataProductLinkMutation();
    const [approveDataOutputLink] = useApproveDataOutputLinkMutation();
    const [rejectDataOutputLink] = useRejectDataOutputLinkMutation();
    const [grantMembershipAccess] = useGrantMembershipAccessMutation();
    const [denyMembershipAccess] = useDenyMembershipAccessMutation();

    const handleAcceptDataProductDatasetLink = useCallback(
        async (request: DataProductDatasetLinkRequest) => {
            try {
                await approveDataProductLink(request).unwrap();
                dispatchMessage({
                    content: t('Dataset request has been successfully approved'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to approve data product dataset link'),
                    type: 'error',
                });
            }
        },
        [approveDataProductLink, t],
    );

    const handleRejectDataProductDatasetLink = useCallback(
        async (request: DataProductDatasetLinkRequest) => {
            try {
                await rejectDataProductLink(request).unwrap();
                dispatchMessage({
                    content: t('Dataset access request has been successfully rejected'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to reject data product dataset link'),
                    type: 'error',
                });
            }
        },
        [rejectDataProductLink, t],
    );

    const handleAcceptDataOutputDatasetLink = useCallback(
        async (request: DataOutputDatasetLinkRequest) => {
            try {
                await approveDataOutputLink(request).unwrap();
                dispatchMessage({
                    content: t('Dataset request has been successfully approved'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to approve data output dataset link'),
                    type: 'error',
                });
            }
        },
        [approveDataOutputLink, t],
    );

    const handleRejectDataOutputDatasetLink = useCallback(
        async (request: DataOutputDatasetLinkRequest) => {
            try {
                await rejectDataOutputLink(request).unwrap();
                dispatchMessage({
                    content: t('Dataset access request has been successfully rejected'),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to reject data output dataset link'),
                    type: 'error',
                });
            }
        },
        [rejectDataOutputLink, t],
    );

    const handleGrantAccessToDataProduct = useCallback(
        async (membershipId: string) => {
            try {
                await grantMembershipAccess({ membershipId }).unwrap();
                dispatchMessage({ content: t('User has been granted access to the data product'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant user access to the data product'), type: 'error' });
            }
        },
        [grantMembershipAccess, t],
    );

    const handleDenyAccessToDataProduct = useCallback(
        async (membershipId: string) => {
            try {
                await denyMembershipAccess({ membershipId }).unwrap();
                dispatchMessage({ content: t('User access to the data product has been denied'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to deny user access to the data product'), type: 'error' });
            }
        },
        [denyMembershipAccess, t],
    );

    const pendingItems = useMemo(() => {
        const colors = {
            [NotificationTypes.DataProductDatasetNotification]: colorWarning,
            [NotificationTypes.DataOutputDatasetNotification]: colorInfo,
            [NotificationTypes.DataProductMembershipNotification]: colorError,
        };

        const userNotifications = pendingActions?.map((userNotification) =>
            createPendingItem({ ...userNotification }, t, colors),
        );
        if (!userNotifications) {
            return [];
        }
        return userNotifications.filter((item) => item !== null);
    }, [pendingActions, t, colorInfo, colorError, colorWarning]);

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

    const handleAccept = (request: ActionResolveRequest) => {
        switch (request.type) {
            case NotificationTypes.DataProductDatasetNotification:
                handleAcceptDataProductDatasetLink(request.request);
                break;
            case NotificationTypes.DataOutputDatasetNotification:
                handleAcceptDataOutputDatasetLink(request.request);
                break;
            case NotificationTypes.DataProductMembershipNotification:
                handleGrantAccessToDataProduct(request.request);
                break;
        }
    };
    const handleDeny = (request: ActionResolveRequest) => {
        switch (request.type) {
            case NotificationTypes.DataProductDatasetNotification:
                handleRejectDataProductDatasetLink(request.request);
                break;
            case NotificationTypes.DataOutputDatasetNotification:
                handleRejectDataOutputDatasetLink(request.request);
                break;
            case NotificationTypes.DataProductMembershipNotification:
                handleDenyAccessToDataProduct(request.request);
                break;
        }
    };

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
                            title={t('Team Request')}
                            requestsCount={itemCountByType[NotificationTypes.DataProductMembershipNotification]}
                            color={colorError}
                            onSelectChange={handleTabChange}
                        />
                        <SelectableTab
                            type={NotificationTypes.DataOutputDatasetNotification}
                            title={t('Data Output')}
                            requestsCount={itemCountByType[NotificationTypes.DataOutputDatasetNotification]}
                            color={colorInfo}
                            onSelectChange={handleTabChange}
                        />
                        <SelectableTab
                            type={NotificationTypes.DataProductDatasetNotification}
                            title={t('Data Product')}
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
                    onAccept={(item) => {
                        handleAccept(item);
                    }}
                    onReject={(item) => {
                        handleDeny(item);
                    }}
                />
            </div>
        </div>
    );
}
