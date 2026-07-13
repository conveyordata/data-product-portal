import { Flex, Input, Table } from 'antd';
import { parseAsString, useQueryState } from 'nuqs';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { acceptRequest, rejectRequest } from '@/components/pending-access-requests-modal/request-handlers.ts';
import { ReviewRequestModal } from '@/components/pending-access-requests-modal/review-request-modal.tsx';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useTableColumns } from '@/pages/product-studio/components/pending-access-requests-tab/use-table-columns.tsx';
import { type TableRow, transformToTableRow } from '@/pages/product-studio/components/requests/request-utils.ts';
import { filterBySearch } from '@/pages/product-studio/components/requests/requests-search.ts';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi.ts';
import type { Request } from '@/types/request-types/request-types.tsx';
import { usePendingActionHandlers } from '@/utils/pending-request.helper.ts';

export function PendingAccessRequestsTab() {
    const { t } = useTranslation();
    const [searchTerm, setSearchTerm] = useQueryState('search', parseAsString.withDefault(''));

    const { data: { pending_actions: pendingRequests = [] } = {} } = useGetUserPendingActionsQuery();
    const [reviewingAction, setReviewingAction] = useState<Request | null>(null);
    const { pagination, handlePaginationChange } = useTablePagination([]);
    const handlers = usePendingActionHandlers();

    const tableData: TableRow[] = useMemo(() => {
        return filterBySearch(pendingRequests, searchTerm).map(transformToTableRow);
    }, [pendingRequests, searchTerm]);

    const handleAccept = (action: Request, decisionNote?: string) => acceptRequest(action, handlers, decisionNote);
    const handleReject = (action: Request, decisionNote?: string) => rejectRequest(action, handlers, decisionNote);
    const handleReview = (action: Request) => setReviewingAction(action);

    const columns = useTableColumns({ onReview: handleReview });

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
