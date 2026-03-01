import type { ColumnsType } from 'antd/es/table';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { PendingAction } from '@/types/pending-actions/pending-request-types';
import {
    type PendingRequestType,
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_DataProductRoleAssignment,
    PendingRequestType_TechnicalAssetOutputPort,
} from '@/types/pending-actions/pending-request-types';
import { formatDate } from '@/utils/date.helper';
import { AccessRequestedCell } from '../components/requests/access-requested-cell';
import { DataProductCell } from '../components/requests/data-product-cell';
import { JustificationCell } from '../components/requests/justification-cell';
import { RequestActions } from '../components/requests/request-actions';
import { RequestTypeBadge } from '../components/requests/request-type-badge';
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
                dataIndex: 'outputPortName',
                key: 'outputPortName',
                sorter: (a, b) => a.outputPortName.localeCompare(b.outputPortName),
                render: (_: string, record: TableRow) => (
                    <AccessRequestedCell action={record.pendingAction} outputPortName={record.outputPortName} />
                ),
            },
            {
                title: t('Requesting Data Product'),
                dataIndex: 'dataProductName',
                key: 'dataProductName',
                sorter: (a, b) => a.dataProductName.localeCompare(b.dataProductName),
                render: (_: string, record: TableRow) => (
                    <DataProductCell action={record.pendingAction} dataProductName={record.dataProductName} />
                ),
            },
            {
                title: t('Type'),
                dataIndex: 'type',
                key: 'type',
                filters: [
                    { text: t('Output Port'), value: PendingRequestType_DataProductOutputPort },
                    { text: t('Data Product'), value: PendingRequestType_DataProductRoleAssignment },
                ],
                onFilter: (value, record) => {
                    if (value === PendingRequestType_DataProductOutputPort) {
                        return (
                            record.type === PendingRequestType_DataProductOutputPort ||
                            record.type === PendingRequestType_TechnicalAssetOutputPort
                        );
                    }
                    return record.type === PendingRequestType_DataProductRoleAssignment;
                },
                render: (type: PendingRequestType) => <RequestTypeBadge type={type} />,
            },
            {
                title: t('Business Justification'),
                dataIndex: 'justification',
                key: 'justification',
                width: 400,
                render: (justification: string | undefined) => <JustificationCell justification={justification} />,
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
