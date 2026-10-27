import { BarChartOutlined } from '@ant-design/icons';
import { Card } from 'antd';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import {
    EmptyState,
    type EmptyStateQuery,
    emptyStateQueryProps,
    hasFailed,
    isAwaitingData,
} from '@/components/empty-state/empty-state.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';

type ChartCardProps = {
    title: string;
    query: EmptyStateQuery;
    hasData: boolean;
    children: ReactNode;
};

export function ChartCard({ title, query, hasData, children }: ChartCardProps) {
    const { t } = useTranslation();
    return (
        <Card title={title}>
            {isAwaitingData(query) ? (
                <LoadingSpinner />
            ) : hasFailed(query) || !hasData ? (
                <EmptyState
                    size="small"
                    icon={<BarChartOutlined />}
                    title={t('No usage recorded')}
                    description={t('Queries against this Output Port in the selected period appear here.')}
                    {...emptyStateQueryProps(query)}
                />
            ) : (
                children
            )}
        </Card>
    );
}
