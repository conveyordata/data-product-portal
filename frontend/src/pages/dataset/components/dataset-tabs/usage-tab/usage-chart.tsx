import { useMemo } from 'react';
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

export function UsageChart({ usageData, curatedQueries, isUsageLoading, areCuratedQueriesLoading }: Props) {
    const { t } = useTranslation();

    const chartData = useMemo(() => {
        if (!usageData?.dataset_query_stats_daily_responses) {
            return [];
        }
        return transformDataForChart(usageData.dataset_query_stats_daily_responses, 'week', t('Unknown'));
    }, [usageData, t]);

    const hasUsageData = Boolean(usageData?.dataset_query_stats_daily_responses?.length);

    return (
        <>
            <QueriesOverTimeChart data={chartData} isLoading={isUsageLoading} hasData={hasUsageData} />
            <CuratedQueriesList queries={curatedQueries} isLoading={areCuratedQueriesLoading} />
        </>
    );
}
