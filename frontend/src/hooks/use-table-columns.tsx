import type { ColumnsType } from 'antd/es/table';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { PendingAction } from '@/types/pending-actions/pending-request-types';
import { formatDate } from '@/utils/date.helper';
import { RequestActions } from '../components/requests/request-actions';
import { RequesterCell } from '../components/requests/requester-cell';
import type { TableRow } from '../utils/request-utils';

type UseTableColumnsParams = {
    onAccept: (action: PendingAction) => void;
    onReject: (action: PendingAction) => void;
};

export function useTableColumns({ onAccept, onReject }: UseTableColumnsParams): ColumnsType<TableRow> {
    const { t } = useTranslation();

    return useMemo(
        () => [
            {
                title: t('Requested by'),
                dataIndex: 'requestedBy',
                key: 'requestedBy',
                sorter: (a, b) => a.requestedBy.name.localeCompare(b.requestedBy.name),
                render: (requestedBy: { name: string; email: string }) => (
                    <RequesterCell name={requestedBy.name} email={requestedBy.email} />
                ),
            },
            {
                title: t('Access Requested'),
                dataIndex: 'description',
                key: 'description',
                sorter: (a, b) => a.description.localeCompare(b.description),
                render: (_: string, record: TableRow) => record.description,
            },
            {
                title: t('Date'),
                dataIndex: 'date',
                key: 'date',
                sorter: (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
                defaultSortOrder: 'descend',
                render: (date: string) => formatDate(date),
            },
            {
                title: t('Actions'),
                key: 'actions',
                render: (_: unknown, record: TableRow) => (
                    <RequestActions action={record.pendingAction} onAccept={onAccept} onReject={onReject} />
                ),
            },
        ],
        [t, onAccept, onReject],
    );
}
