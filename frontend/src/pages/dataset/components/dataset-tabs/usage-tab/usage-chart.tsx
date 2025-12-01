import { Flex, Tabs } from 'antd';
import { type ReactNode, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import type { DatasetCuratedQueryContract } from '@/types/dataset';
import type { DatasetQueryStatsDailyResponses } from '@/types/dataset/dataset-query-stats-daily.contract';
import { transformDataForChart } from './components/chart-data.utils';
import { CuratedQueriesList } from './components/curated-queries-list';
import { QueriesOverTimeChart } from './components/queries-over-time-chart';

type Props = {
    usageData?: DatasetQueryStatsDailyResponses;
    curatedQueries?: DatasetCuratedQueryContract[];
    isUsageLoading: boolean;
    areCuratedQueriesLoading: boolean;
};

enum UsageTabKeys {
    UsageStatistics = 'usage-statistics',
    CuratedQueries = 'curated-queries',
}

type Tab = {
    label: string;
    key: UsageTabKeys;
    children: ReactNode;
};

export function UsageChart({ usageData, curatedQueries, isUsageLoading, areCuratedQueriesLoading }: Props) {
    const { t } = useTranslation();

    const chartData = useMemo(() => {
        if (!usageData?.dataset_query_stats_daily_responses) {
            return [];
        }
        return transformDataForChart(usageData.dataset_query_stats_daily_responses, t('Unknown'));
    }, [usageData, t]);

    const hasUsageData = Boolean(usageData?.dataset_query_stats_daily_responses?.length);

    const tabs: Tab[] = useMemo(() => {
        return [
            {
                label: t('Usage Statistics'),
                key: UsageTabKeys.UsageStatistics,
                children: <QueriesOverTimeChart data={chartData} isLoading={isUsageLoading} hasData={hasUsageData} />,
            },
            {
                label: t('Curated Queries'),
                key: UsageTabKeys.CuratedQueries,
                children: <CuratedQueriesList queries={curatedQueries} isLoading={areCuratedQueriesLoading} />,
            },
        ];
    }, [chartData, curatedQueries, areCuratedQueriesLoading, hasUsageData, isUsageLoading, t]);

    return (
        <Flex vertical gap={24}>
            <Tabs
                defaultActiveKey={UsageTabKeys.UsageStatistics}
                items={tabs.map(({ key, label, children }) => ({
                    label,
                    key,
                    children,
                }))}
                size="middle"
            />
        </Flex>
    );
}
