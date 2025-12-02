import { Empty, Flex, Select, Spin, Tabs, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
    useGetDatasetQueryCuratedQueriesQuery,
    useGetDatasetQueryStatsDailyQuery,
} from '@/store/features/datasets/datasets-api-slice';
import type { DatasetQueryStatsGranularity } from '@/types/dataset/dataset-query-stats-daily.contract';
import { aggregateQueriesPerConsumer, transformDataForChart } from './components/chart-data.utils';
import { CuratedQueriesList } from './components/curated-queries-list';
import { QueriesOverTimeChart } from './components/queries-over-time-chart';
import { QueriesPerConsumerChart } from './components/queries-per-consumer-chart';
import styles from './usage-tab.module.scss';

type Props = {
    datasetId: string;
};

enum UsageTabKeys {
    UsageStatistics = 'usage-statistics',
    CuratedQueries = 'curated-queries',
}

export function UsageTab({ datasetId }: Props) {
    const { t } = useTranslation();
    const [granularity, setGranularity] = useState<DatasetQueryStatsGranularity>('week');
    const longestDayRange = 365;
    const [dayRange, setDayRange] = useState<number>(longestDayRange);

    const granularityOptions = useMemo(
        () => [
            { label: t('Day'), value: 'day' },
            { label: t('Week'), value: 'week' },
            { label: t('Month'), value: 'month' },
        ],
        [t],
    );

    const { data, isLoading, isFetching } = useGetDatasetQueryStatsDailyQuery({
        datasetId,
        granularity,
        dayRange,
    });

    const { data: curatedQueries, isLoading: areCuratedQueriesLoading } = useGetDatasetQueryCuratedQueriesQuery(
        datasetId,
        {
            skip: !datasetId,
        },
    );

    const isLoadingState = isLoading || isFetching;
    const responses = data?.dataset_query_stats_daily_responses;
    const hasUsageData = Boolean(responses?.length);
    const unknownLabel = t('Unknown');

    const chartData = useMemo(() => {
        if (!responses?.length) {
            return [];
        }
        return transformDataForChart(responses, dayRange, granularity, unknownLabel);
    }, [responses, dayRange, granularity, unknownLabel]);

    const consumerTotals = useMemo(() => aggregateQueriesPerConsumer(chartData), [chartData]);

    const usageStatisticsContent = (
        <>
            {isLoadingState && !hasUsageData ? (
                <Flex vertical className={styles.container} align="center" justify="center">
                    <Spin size="large" />
                </Flex>
            ) : !isLoadingState && !hasUsageData ? (
                <Flex vertical className={styles.container} align="center" justify="center">
                    <Empty description={t('No usage data available for this dataset')} />
                </Flex>
            ) : (
                <Flex vertical className={styles.container}>
                    <Flex className={styles.filters} gap={24} wrap>
                        <Flex vertical className={styles.filterGroup}>
                            <Typography.Text>{t('Granularity')}</Typography.Text>
                            <Select value={granularity} onChange={setGranularity} options={granularityOptions} />
                        </Flex>
                        <Flex vertical className={styles.filterGroup}>
                            <Typography.Text>{t('Time Range')}</Typography.Text>
                            <Select
                                value={dayRange}
                                onChange={(value) => setDayRange(Number(value))}
                                options={[
                                    { label: t('Last 30 days'), value: 30 },
                                    { label: t('Last 90 days'), value: 90 },
                                    { label: t('Last year'), value: longestDayRange },
                                ]}
                            />
                        </Flex>
                    </Flex>
                    <Flex className={styles.chartsGrid} gap={32}>
                        <QueriesOverTimeChart
                            className={styles.chartCard}
                            data={chartData}
                            isLoading={isLoadingState}
                            hasData={hasUsageData}
                        />
                        <QueriesPerConsumerChart
                            className={styles.chartCard}
                            data={consumerTotals}
                            isLoading={isLoadingState}
                            hasData={hasUsageData}
                        />
                    </Flex>
                </Flex>
            )}
        </>
    );

    const curatedQueriesContent = (
        <CuratedQueriesList queries={curatedQueries?.dataset_curated_queries} isLoading={areCuratedQueriesLoading} />
    );

    return (
        <Tabs
            defaultActiveKey={UsageTabKeys.UsageStatistics}
            items={[
                {
                    key: UsageTabKeys.UsageStatistics,
                    label: t('Usage Statistics'),
                    children: usageStatisticsContent,
                },
                {
                    key: UsageTabKeys.CuratedQueries,
                    label: t('Curated Queries'),
                    children: curatedQueriesContent,
                },
            ]}
            size="middle"
        />
    );
}
