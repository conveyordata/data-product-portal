import { Flex, Input, Table } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ReviewRequestModal } from '@/components/requests/review-request-modal';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi';
import type { PendingAction } from '@/types/pending-actions/pending-request-types';
import {
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_DataProductRoleAssignment,
    PendingRequestType_TechnicalAssetOutputPort,
} from '@/types/pending-actions/pending-request-types';
import { usePendingActionHandlers } from '@/utils/pending-request.helper';
import { acceptRequest, rejectRequest } from '../../../../components/requests/request-handlers';
import { type TableRow, transformToTableRow } from '../../../../components/requests/request-utils';
import { useTableColumns } from '../../../../components/requests/use-table-columns';

function filterBySearch(requests: PendingAction[], searchTerm: string): PendingAction[] {
    if (!searchTerm) return requests;

    const lowerSearch = searchTerm.toLowerCase();

    return requests.filter((action) => {
        // Check data link requests
        if (
            action.pending_action_type === PendingRequestType_DataProductOutputPort ||
            action.pending_action_type === PendingRequestType_TechnicalAssetOutputPort
        ) {
            return (
                action.output_port.name.toLowerCase().includes(lowerSearch) ||
                ('data_product' in action && action.data_product.name.toLowerCase().includes(lowerSearch)) ||
                action.requested_by.first_name.toLowerCase().includes(lowerSearch) ||
                action.requested_by.last_name.toLowerCase().includes(lowerSearch) ||
                action.requested_by.email.toLowerCase().includes(lowerSearch)
            );
        }

        // Check role assignment requests
        if (action.pending_action_type === PendingRequestType_DataProductRoleAssignment) {
            return (
                action.user.first_name.toLowerCase().includes(lowerSearch) ||
                action.user.last_name.toLowerCase().includes(lowerSearch) ||
                action.user.email.toLowerCase().includes(lowerSearch) ||
                action.role?.name.toLowerCase().includes(lowerSearch)
            );
        }

        return false;
    });
}

export function PendingAccessRequestsView() {
    const { t } = useTranslation();
    const [searchTerm, setSearchTerm] = useState('');

    const { data: { pending_actions: pendingRequests = [] } = {} } = useGetUserPendingActionsQuery();
    const [reviewingAction, setReviewingAction] = useState<PendingAction | null>(null);
    const { pagination, handlePaginationChange } = useTablePagination([]);
    const handlers = usePendingActionHandlers();

    const filteredData = useMemo(() => {
        return filterBySearch(pendingRequests, searchTerm);
    }, [pendingRequests, searchTerm]);

    const tableData: TableRow[] = useMemo(() => {
        return filteredData.map(transformToTableRow);
    }, [filteredData]);

    const handleAccept = (action: PendingAction) => acceptRequest(action, handlers);
    const handleReject = (action: PendingAction) => rejectRequest(action, handlers);
    const handleReview = (action: PendingAction) => setReviewingAction(action);

    const columns = useTableColumns({
        onReview: handleReview,
    });

    return (
        <Flex vertical gap="small">
            {/* Toolbar with segmented controls and search */}
            <Input.Search
                placeholder={t('Search requests...')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ maxWidth: 400 }}
                allowClear
            />
            <Table
                columns={columns}
                dataSource={tableData}
                size="small"
                pagination={{
                    ...pagination,
                    onChange: (page, pageSize) => {
                        handlePaginationChange({ current: page, pageSize });
                    },
                }}
                locale={{
                    emptyText: t('No pending requests.'),
                }}
            />
            <ReviewRequestModal
                action={reviewingAction}
                open={reviewingAction !== null}
                onClose={() => setReviewingAction(null)}
                onAccept={handleAccept}
                onReject={handleReject}
            />
        </Flex>
    );
}
