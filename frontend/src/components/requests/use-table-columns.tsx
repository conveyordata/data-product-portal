import { Space, theme } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { PendingAction } from '@/types/pending-actions/pending-request-types';
import { formatDate } from '@/utils/date.helper';
import { UserAvatarWithEmail } from '../user-avatar/user-avatar-with-email.component';
import type { TableRow } from './request-utils';
import { ReviewButton } from './review-button';

type UseTableColumnsParams = {
    onReview: (action: PendingAction) => void;
};

export function useTableColumns({ onReview }: UseTableColumnsParams): ColumnsType<TableRow> {
    const { t } = useTranslation();
    const { useToken } = theme;
    const { token } = useToken();

    const secondaryColor = token.colorPrimary;

    return useMemo(
        () => [
            {
                title: t('Requested by'),
                dataIndex: 'requestedBy',
                key: 'requestedBy',
                sorter: (a, b) => a.requestedBy?.email.localeCompare(b.requestedBy?.email || '') || 0,
                render: (requestedBy) => {
                    return (
                        <Space size="small">
                            <UserAvatarWithEmail user={requestedBy} color={secondaryColor} />
                        </Space>
                    );
                },
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
                    <ReviewButton action={record.pendingAction} onReview={onReview} />
                ),
            },
        ],
        [t, onReview, secondaryColor],
    );
}
