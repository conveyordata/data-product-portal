import { usePostHog } from '@posthog/react';
import { Pagination } from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PosthogEvents } from '@/constants/posthog.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import {
    type CustomPendingRequestsTabKey,
    SelectableTabs,
} from '@/pages/home/components/pending-approvals-inbox/pending-approvals-menu-tabs.tsx';
import {
    type PendingRequestType,
    PendingRequestTypeValues,
} from '@/pages/home/components/pending-approvals-inbox/pending-approvals-types.tsx';
import type {
    DataProductOutputPortPendingAction,
    DataProductRoleAssignmentPendingAction,
    TechnicalAssetOutputPortPendingAction,
} from '@/store/api/services/generated/usersApi.ts';
import styles from './pending-approvals-inbox.module.scss';
import { PendingApprovalsList } from './pending-approvals-list.tsx';

export type PendingAction =
    | DataProductOutputPortPendingAction
    | DataProductRoleAssignmentPendingAction
    | TechnicalAssetOutputPortPendingAction;

type Props = {
    pendingApprovals: PendingAction[];
};
export function PendingApprovalsInbox({ pendingApprovals }: Props) {
    const { t } = useTranslation();
    const posthog = usePostHog();
    const [activeTab, setActiveTab] = useState<CustomPendingRequestsTabKey>('all');

    const selectedTypes: readonly PendingRequestType[] = useMemo(() => {
        switch (activeTab) {
            case 'all':
                return PendingRequestTypeValues;
            case 'dataProduct':
                return ['DataProductRoleAssignment'];
            case 'dataset':
                return ['DataProductOutputPort', 'TechnicalAssetOutputPort'];
        }
    }, [activeTab]);

    const filteredPendingActions = useMemo(() => {
        return pendingApprovals.filter(
            (item) => item.pending_action_type && selectedTypes.includes(item.pending_action_type),
        );
    }, [pendingApprovals, selectedTypes]);

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
    };

    return (
        <>
            <SelectableTabs
                activeKey={activeTab}
                onTabChange={handleTabChange}
                extra={
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
                }
                style={{ paddingInline: 20 }}
            />

            <PendingApprovalsList pendingActions={filteredPendingActions} pagination={pagination} />
        </>
    );
}
