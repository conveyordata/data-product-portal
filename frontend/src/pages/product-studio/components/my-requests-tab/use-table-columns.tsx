import { Badge, Space, theme } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import EllipsisParagraph from '@/components/ellipsis-paragraph/ellipsis-paragraph.component.tsx';
import { UserAvatarWithEmail } from '@/components/user-avatar/user-avatar-with-email.component.tsx';
import type { TableRow } from '@/pages/product-studio/components/requests/request-utils.ts';
import type { DecisionStatus, InputPortRequestDecision } from '@/store/api/services/generated/usersApi.ts';
import { formatDate } from '@/utils/date.helper.ts';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper.ts';

export function useTableColumns(): ColumnsType<TableRow> {
    const { t } = useTranslation();
    const { useToken } = theme;
    const { token } = useToken();

    const secondaryColor = token.colorPrimary;

    return useMemo(
        () => [
            {
                title: t('Decision'),
                dataIndex: 'decision',
                key: 'decision',
                render: (decision: DecisionStatus | InputPortRequestDecision) => (
                    <Badge status={getDecisionStatusBadgeStatus(decision)} text={getDecisionStatusLabel(t, decision)} />
                ),
            },
            {
                title: t('Decided by'),
                dataIndex: 'decidedBy',
                key: 'decidedBy',
                sorter: (a, b) => a.decidedBy?.email.localeCompare(b.decidedBy?.email || '') || 0,
                render: (decidedBy) => {
                    if (decidedBy == null) {
                        return null;
                    }
                    return (
                        <Space size="small">
                            <UserAvatarWithEmail user={decidedBy} color={secondaryColor} />
                        </Space>
                    );
                },
            },
            {
                title: t('Decision note'),
                dataIndex: 'decisionNote',
                render: (_, { decisionNote }) => <EllipsisParagraph text={decisionNote} />,
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
        ],
        [t, secondaryColor],
    );
}
