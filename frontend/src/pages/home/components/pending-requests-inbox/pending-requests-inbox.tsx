import { CheckCircleOutlined } from '@ant-design/icons';
import { Badge, Col, Empty, Flex, Pagination, Typography, theme } from 'antd';
import type { TFunction } from 'i18next';
import { type ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import posthog from '@/config/posthog-config';
import { PosthogEvents } from '@/constants/posthog.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { useGetPendingActionsQuery } from '@/store/features/pending-actions/pending-actions-api-slice';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import {
    type ActionResolveRequest,
    type PendingAction,
    PendingActionTypes,
} from '@/types/pending-actions/pending-actions';
import { usePendingActionHandlers } from '@/utils/pending-request.helper';
import styles from './pending-requests-inbox.module.scss';
import { type PendingActionItem, PendingRequestsList } from './pending-requests-list';
import { type CustomPendingRequestsTabKey, SelectableTabs } from './pending-requests-menu-tabs';

const createPendingItem = (action: PendingAction, t: TFunction, color: string): PendingActionItem | null => {
    let link: string;
    let description: ReactElement;
    let navigatePath: string;
    let date: string;
    let author: string;
    let initials: string;
    let message: ReactElement;
    let tag: ReactElement;
    let type: PendingActionTypes;
    let request: ActionResolveRequest;
    let icon: ReactElement;

    function getInitials(firstName: string, lastName: string) {
        return (firstName?.charAt(0) || '') + (lastName ? lastName.charAt(0) : '');
    }

    switch (action.pending_action_type) {
        case PendingActionTypes.DataProductDataset:
            icon = <DatasetOutlined />;
            link = createDataProductIdPath(action.data_product_id);
            description = (
                <Typography.Text strong>
                    {t('Request for')} <strong className={styles.bolder}>{t('read access')}</strong>{' '}
                    {t('from the data product')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        <strong>{action.data_product.name}</strong>
                    </Link>
                </Typography.Text>
            );
            message = (
                <Typography.Text>
                    {t('Accepting will grant the data product read access on the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.dataset_id)}>
                        {action.dataset.name}
                    </Link>{' '}
                    {t('dataset.')}
                </Typography.Text>
            );
            tag = (
                <Typography.Text
                    style={{
                        color: color,
                    }}
                    strong
                >
                    {t('{{name}} Dataset', { name: action.dataset.name })}
                </Typography.Text>
            );
            navigatePath = createDatasetIdPath(action.dataset_id, DatasetTabKeys.DataProduct);
            date = action.requested_on;
            author = `${action.requested_by.first_name} ${action.requested_by.last_name}`;
            initials = getInitials(action.requested_by.first_name, action.requested_by.last_name);
            type = PendingActionTypes.DataProductDataset as PendingActionTypes.DataProductDataset;
            request = {
                type: PendingActionTypes.DataProductDataset as PendingActionTypes.DataProductDataset,
                request: {
                    id: action.id,
                    data_product_id: action.data_product_id,
                    dataset_id: action.dataset_id,
                },
            };
            break;

        case PendingActionTypes.DataOutputDataset:
            icon = <DatasetOutlined color="" />;
            link = createDataOutputIdPath(action.data_output_id, action.data_output.owner_id);
            description = (
                <Typography.Text strong>
                    {t('Request for')} <strong className={styles.bolder}>{t('the creation of a link')}</strong>{' '}
                    {t('coming from the technical asset')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.dataset_id)}>
                        <strong>{action.data_output.name}</strong>
                    </Link>
                </Typography.Text>
            );
            message = (
                <Typography.Text>
                    {t('Accepting will create a link from the technical asset to the')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.dataset_id)}>
                        {action.dataset.name}
                    </Link>{' '}
                    {t('dataset.')}
                </Typography.Text>
            );
            tag = (
                <Typography.Text
                    style={{
                        color: color,
                    }}
                    strong
                >
                    {t('{{name}} Dataset', { name: action.dataset.name })}
                </Typography.Text>
            );
            navigatePath = createDatasetIdPath(action.dataset_id, DatasetTabKeys.DataOutput);
            date = action.requested_on;
            author = `${action.requested_by.first_name} ${action.requested_by.last_name}`;
            initials = getInitials(action.requested_by.first_name, action.requested_by.last_name);
            type = PendingActionTypes.DataOutputDataset as PendingActionTypes.DataOutputDataset;
            request = {
                type: PendingActionTypes.DataOutputDataset as PendingActionTypes.DataOutputDataset,
                request: {
                    id: action.id,
                    data_output_id: action.data_output_id,
                    dataset_id: action.dataset_id,
                },
            };
            break;

        case PendingActionTypes.DataProductRoleAssignment:
            icon = <DataProductOutlined />;
            link = createDataProductIdPath(action.data_product.id);
            description = (
                <Typography.Text strong>
                    {t('Request for ')} <strong className={styles.bolder}>{t('team membership')}</strong> {t('from')}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={'/'}>
                        <strong>
                            {action.user.first_name} {action.user.last_name}
                        </strong>
                    </Link>
                </Typography.Text>
            );
            message = (
                <Typography.Text>
                    {t('Accepting will grant the user the role of {{role}} in the', {
                        role: action.role.name,
                        firstName: action.user.first_name,
                        lastName: action.user.last_name,
                    })}{' '}
                    <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.data_product.id)}>
                        {action.data_product.name}
                    </Link>{' '}
                    {t('data product.')}
                </Typography.Text>
            );
            tag = (
                <Typography.Text
                    style={{
                        color: color,
                    }}
                    strong
                >
                    {t('{{name}} Data Product', { name: action.data_product.name })}
                </Typography.Text>
            );
            navigatePath = createDataProductIdPath(action.data_product.id, DataProductTabKeys.Team);
            date = action.requested_on ?? '';
            author = `${action.user.first_name} ${action.user.last_name}`;
            initials = getInitials(action.user.first_name, action.user.last_name);
            type = PendingActionTypes.DataProductRoleAssignment as PendingActionTypes.DataProductRoleAssignment;
            request = {
                type: PendingActionTypes.DataProductRoleAssignment as PendingActionTypes.DataProductRoleAssignment,
                request: { assignment_id: action.id, data_product_id: action.data_product.id },
            };
            break;

        default:
            return null;
    }

    return {
        key: type + action.id,
        description: description,
        navigatePath: navigatePath,
        date: date,
        author: author,
        initials: initials,
        message: message,
        color: color,
        tag: tag,
        type: action.pending_action_type,
        request: request,
        icon: icon,
    };
};

export function PendingRequestsInbox() {
    const { t } = useTranslation();
    const {
        token: { colorPrimary: dataProductColor, colorPrimaryActive: datasetColor },
    } = theme.useToken();
    const [activeTab, setActiveTab] = useState<CustomPendingRequestsTabKey>('all');
    const [selectedTypes, setSelectedTypes] = useState<Set<PendingActionTypes>>(new Set());

    const { data: pendingActions, isFetching } = useGetPendingActionsQuery();

    const {
        handleAcceptDataProductDatasetLink,
        handleRejectDataProductDatasetLink,
        handleAcceptDataOutputDatasetLink,
        handleRejectDataOutputDatasetLink,
        handleGrantAccessToDataProduct,
        handleDenyAccessToDataProduct,
    } = usePendingActionHandlers();

    const pendingItems = useMemo(() => {
        const items = pendingActions?.map((action) =>
            createPendingItem(
                action,
                t,
                action.pending_action_type === PendingActionTypes.DataOutputDataset ||
                    action.pending_action_type === PendingActionTypes.DataProductDataset
                    ? datasetColor
                    : dataProductColor,
            ),
        );

        return (items ?? [])
            .filter((item) => item !== null)
            .sort((a, b) => {
                if (!a?.date || !b?.date) {
                    return 0;
                }
                return new Date(a.date).getTime() - new Date(b.date).getTime();
            });
    }, [pendingActions, t, dataProductColor, datasetColor]);

    const { pagination, handlePaginationChange, resetPagination } = useTablePagination([]);

    const handlePageChange = (page: number, pageSize: number) => {
        handlePaginationChange({
            current: page,
            pageSize,
        });
    };

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
        resetPagination();
    }, [resetPagination]);

    const handleTabChange = (key: CustomPendingRequestsTabKey) => {
        posthog.capture(PosthogEvents.REQUESTS_TAB_CLICKED, {
            tab_name: key,
        });
        setActiveTab(key);

        const typesSet = new Set<PendingActionTypes>();
        if (key === 'all') {
            for (const type of Object.values(PendingActionTypes)) {
                typesSet.add(type);
            }
        } else if (key === 'dataProduct') {
            typesSet.add(PendingActionTypes.DataProductRoleAssignment);
        } else if (key === 'dataset') {
            typesSet.add(PendingActionTypes.DataProductDataset);
            typesSet.add(PendingActionTypes.DataOutputDataset);
        }

        setSelectedTypes(typesSet);
    };

    const handleAccept = (request: ActionResolveRequest) => {
        posthog.capture(PosthogEvents.REQUESTS_ACCEPT);

        switch (request.type) {
            case PendingActionTypes.DataProductDataset:
                handleAcceptDataProductDatasetLink(request.request);
                break;
            case PendingActionTypes.DataOutputDataset:
                handleAcceptDataOutputDatasetLink(request.request);
                break;
            case PendingActionTypes.DataProductRoleAssignment:
                handleGrantAccessToDataProduct(request.request);
                break;
        }
    };
    const handleDeny = (request: ActionResolveRequest) => {
        posthog.capture(PosthogEvents.REQUESTS_REJECT);

        switch (request.type) {
            case PendingActionTypes.DataProductDataset:
                handleRejectDataProductDatasetLink(request.request);
                break;
            case PendingActionTypes.DataOutputDataset:
                handleRejectDataOutputDatasetLink(request.request);
                break;
            case PendingActionTypes.DataProductRoleAssignment:
                handleDenyAccessToDataProduct(request.request);
                break;
        }
    };

    if (pendingItems.length === 0 && !isFetching) {
        return (
            <div className={styles.requestsInbox}>
                <Typography.Title level={1} className={styles.welcomeContent}>
                    {t('Welcome back')}
                </Typography.Title>
                <Empty
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                    description={
                        <Typography.Text>
                            <CheckCircleOutlined /> {t('You have no requests to handle.')}
                        </Typography.Text>
                    }
                />
            </div>
        );
    }

    if (isFetching) return <LoadingSpinner />;

    return (
        <div className={styles.requestsInbox}>
            <Flex align="flex-end" justify="space-between">
                <Typography.Title level={3}>
                    {t('Pending Requests')}
                    <Badge count={slicedPendingActionItems.length} color="gray" className={styles.requestsInfo} />
                </Typography.Title>{' '}
            </Flex>
            <Flex align="center" justify="space-between">
                <Col span={24}>
                    <SelectableTabs activeKey={activeTab} onTabChange={handleTabChange} />
                    <Pagination
                        current={pagination.current}
                        pageSize={pagination.pageSize}
                        total={slicedPendingActionItems.length}
                        onChange={handlePageChange}
                        size="small"
                        className={styles.pagination}
                        showTotal={(total, range) =>
                            t('Showing {{range0}}-{{range1}} of {{total}} pending requests', {
                                range0: range[0],
                                range1: range[1],
                                total: total,
                            })
                        }
                    />
                </Col>
            </Flex>

            <Flex vertical>
                <PendingRequestsList
                    pendingActionItems={slicedPendingActionItems}
                    pagination={pagination}
                    onAccept={(item) => {
                        handleAccept(item);
                    }}
                    onReject={(item) => {
                        handleDeny(item);
                    }}
                />
            </Flex>
        </div>
    );
}
