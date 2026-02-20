import { CheckCircleOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import { Badge, Col, Empty, Flex, Pagination, Typography } from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { PosthogEvents } from '@/constants/posthog.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import {
    type PendingRequestType,
    PendingRequestTypeValues,
} from '@/pages/home/components/pending-requests-inbox/pending-request-types.tsx';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi.ts';
import styles from './pending-requests-inbox.module.scss';
import { PendingRequestsList } from './pending-requests-list';
import { type CustomPendingRequestsTabKey, SelectableTabs } from './pending-requests-menu-tabs';

export function PendingRequestsInbox() {
    const { t } = useTranslation();
    const posthog = usePostHog();
    const [activeTab, setActiveTab] = useState<CustomPendingRequestsTabKey>('all');
    const [selectedTypes, setSelectedTypes] = useState<Set<PendingRequestType>>(new Set());

    const { data: { pending_actions: pendingActions = [] } = {}, isFetching } = useGetUserPendingActionsQuery();

    const filteredPendingActions = useMemo(() => {
        if (!pendingActions) return [];
        return selectedTypes.size === 0
            ? pendingActions
            : pendingActions.filter((item) => item.pending_action_type && selectedTypes.has(item.pending_action_type));
    }, [pendingActions, selectedTypes]);

    const { pagination, handlePaginationChange, resetPagination } = useTablePagination([]);

    const handlePageChange = (page: number, pageSize: number) => {
        handlePaginationChange({
            current: page,
            pageSize,
        });
    };

    useEffect(() => {
        resetPagination();
    }, [resetPagination]);

    const handleTabChange = (key: CustomPendingRequestsTabKey) => {
        posthog.capture(PosthogEvents.REQUESTS_TAB_CLICKED, {
            tab_name: key,
        });
        setActiveTab(key);

        const typesSet = new Set<PendingRequestType>();
        if (key === 'all') {
            for (const t of PendingRequestTypeValues) {
                typesSet.add(t);
            }
        } else if (key === 'dataProduct') {
            typesSet.add('DataProductRoleAssignment');
        } else if (key === 'dataset') {
            typesSet.add('DataProductOutputPort');
            typesSet.add('TechnicalAssetOutputPort');
        }

        setSelectedTypes(typesSet);
    };

    if (pendingActions?.length === 0 && !isFetching) {
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
                    <Badge count={filteredPendingActions.length} color="gray" className={styles.requestsInfo} />
                </Typography.Title>
            </Flex>
            <Flex align="center" justify="space-between">
                <Col span={24}>
                    <SelectableTabs activeKey={activeTab} onTabChange={handleTabChange} />
                    <Pagination
                        current={pagination.current}
                        pageSize={pagination.pageSize}
                        total={filteredPendingActions.length}
                        onChange={handlePageChange}
                        size="small"
                        className={styles.pagination}
                        showTotal={(total, range) =>
                            t('Showing {{range0}}-{{range1}} of {{count}} pending requests', {
                                range0: range[0],
                                range1: range[1],
                                count: total,
                            })
                        }
                    />
                </Col>
            </Flex>

            <PendingRequestsList pendingActions={filteredPendingActions} pagination={pagination} />
        </div>
    );
}
