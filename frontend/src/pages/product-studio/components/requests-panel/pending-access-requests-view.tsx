import { Table } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { type PendingAction, PendingActionTypes } from '@/types/pending-actions/pending-actions';
import { usePendingActionHandlers } from '@/utils/pending-request.helper';
import { ExpandedRequestDetails } from '../../../../components/requests/expanded-request-details';
import { useTableColumns } from '../../../../hooks/use-table-columns';
import { acceptRequest, rejectRequest } from '../../../../utils/request-handlers';
import { type TableRow, transformToTableRow } from '../../../../utils/request-utils';

type Props = {
    pendingRequests: PendingAction[];
    typeFilter: 'all' | 'outputPort' | 'dataProduct';
    searchTerm: string;
};

function filterByType(requests: PendingAction[], typeFilter: Props['typeFilter']): PendingAction[] {
    if (typeFilter === 'outputPort') {
        return requests.filter(
            (action) =>
                action.pending_action_type === PendingActionTypes.DataProductDataset ||
                action.pending_action_type === PendingActionTypes.DataOutputDataset,
        );
    }

    if (typeFilter === 'dataProduct') {
        return requests.filter(
            (action) =>
                action.pending_action_type === PendingActionTypes.DataProductRoleAssignment ||
                action.pending_action_type === PendingActionTypes.DatasetRoleAssignment,
        );
    }

    return requests;
}

function filterBySearch(requests: PendingAction[], searchTerm: string): PendingAction[] {
    if (!searchTerm) return requests;

    const lowerSearch = searchTerm.toLowerCase();

    return requests.filter((action) => {
        // Check data link requests
        if (
            action.pending_action_type === PendingActionTypes.DataProductDataset ||
            action.pending_action_type === PendingActionTypes.DataOutputDataset
        ) {
            return (
                action.dataset.name.toLowerCase().includes(lowerSearch) ||
                ('data_product' in action && action.data_product.name.toLowerCase().includes(lowerSearch)) ||
                action.requested_by.first_name.toLowerCase().includes(lowerSearch) ||
                action.requested_by.last_name.toLowerCase().includes(lowerSearch) ||
                action.requested_by.email.toLowerCase().includes(lowerSearch)
            );
        }

        // Check role assignment requests
        if (
            action.pending_action_type === PendingActionTypes.DataProductRoleAssignment ||
            action.pending_action_type === PendingActionTypes.DatasetRoleAssignment
        ) {
            return (
                action.user.first_name.toLowerCase().includes(lowerSearch) ||
                action.user.last_name.toLowerCase().includes(lowerSearch) ||
                action.user.email.toLowerCase().includes(lowerSearch)
            );
        }

        return false;
    });
}

export function PendingAccessRequestsView({ pendingRequests, typeFilter, searchTerm }: Props) {
    const { t } = useTranslation();
    const [expandedRowKeys, setExpandedRowKeys] = useState<string[]>([]);
    const { pagination, handlePaginationChange } = useTablePagination([]);
    const handlers = usePendingActionHandlers();

    const filteredData = useMemo(() => {
        const byType = filterByType(pendingRequests, typeFilter);
        return filterBySearch(byType, searchTerm);
    }, [pendingRequests, typeFilter, searchTerm]);

    const tableData: TableRow[] = useMemo(() => {
        return filteredData.map(transformToTableRow);
    }, [filteredData]);

    const handleAccept = (action: PendingAction) => acceptRequest(action, handlers);
    const handleReject = (action: PendingAction) => rejectRequest(action, handlers);

    const columns = useTableColumns({
        onAccept: handleAccept,
        onReject: handleReject,
    });

    return (
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
            expandable={{
                expandedRowRender: (record: TableRow) => <ExpandedRequestDetails action={record.pendingAction} />,
                expandedRowKeys,
                onExpand: (expanded, record) => {
                    setExpandedRowKeys(expanded ? [record.key] : []);
                },
            }}
            locale={{
                emptyText: t('No pending requests.'),
            }}
        />
    );
}
