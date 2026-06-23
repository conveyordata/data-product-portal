import { Flex, Input, Table } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import {
    acceptRequest,
    rejectRequest,
} from '@/pages/product-studio/components/requests-panel/pending-access-requests-modal/request-handlers.ts';
import {
    type TableRow,
    transformToTableRow,
} from '@/pages/product-studio/components/requests-panel/pending-access-requests-modal/request-utils.ts';
import { ReviewRequestModal } from '@/pages/product-studio/components/requests-panel/pending-access-requests-modal/review-request-modal.tsx';
import { useTableColumns } from '@/pages/product-studio/components/requests-panel/pending-access-requests-modal/use-table-columns.tsx';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi.ts';
import type { PendingAction } from '@/types/pending-actions/pending-request-types.tsx';
import {
    PendingRequestType_DataProductRoleAssignment,
    PendingRequestType_InputPort,
    PendingRequestType_TechnicalAssetOutputPort,
} from '@/types/pending-actions/pending-request-types.tsx';
import { usePendingActionHandlers } from '@/utils/pending-request.helper.ts';

function filterBySearch(requests: PendingAction[], searchTerm: string): PendingAction[] {
    if (!searchTerm) return requests;

    const lowerSearch = searchTerm.toLowerCase();

    return requests.filter((action) => {
        // Check data link requests
        if (
            action.pending_action_type === PendingRequestType_InputPort ||
            action.pending_action_type === PendingRequestType_TechnicalAssetOutputPort
        ) {
            return (
                action.output_port.name.toLowerCase().includes(lowerSearch) ||
                ('consuming_abstract_data_product' in action &&
                    action.consuming_abstract_data_product.name.toLowerCase().includes(lowerSearch)) ||
                ('technical_asset' in action && action.technical_asset.name.toLowerCase().includes(lowerSearch)) ||
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

    const handleAccept = (action: PendingAction, reasoning?: string) => acceptRequest(action, handlers, reasoning);
    const handleReject = (action: PendingAction, reasoning?: string) => rejectRequest(action, handlers, reasoning);
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
