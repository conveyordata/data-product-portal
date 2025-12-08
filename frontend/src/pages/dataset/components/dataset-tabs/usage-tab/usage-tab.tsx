import { Col, Empty, Flex, Radio, type RadioChangeEvent, Row, Spin, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
    useGetDatasetQueryCuratedQueriesQuery,
    useGetDatasetQueryStatsDailyQuery,
} from '@/store/features/datasets/datasets-api-slice';

import type { DatasetQueryStatsGranularity } from '@/types/dataset/dataset-query-stats-daily.contract';
import {
    aggregateQueriesPerConsumer,
    createColorScaleConfig,
    getUniqueConsumers,
    transformDataForChart,
} from './components/chart-data.utils';
import { CuratedQueriesList } from './components/curated-queries-list';
import { QueriesOverTimeChart } from './components/queries-over-time-chart';
import { QueriesPerConsumerChart } from './components/queries-per-consumer-chart';

type Props = {
    datasetId: string;
};

function getGranularityFromDayRange(dayRange: number): DatasetQueryStatsGranularity {
    if (dayRange === 365) {
        return 'month';
    }
    if (dayRange === 90) {
        return 'week';
    }
    return 'day';
}

export function UsageTab({ datasetId }: Props) {
    const { t } = useTranslation();
    const longestDayRange = 365;
    const [dayRange, setDayRange] = useState<number>(longestDayRange);
    const granularity = useMemo(() => getGranularityFromDayRange(dayRange), [dayRange]);

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
        return transformDataForChart(responses, granularity, unknownLabel);
    }, [responses, granularity, unknownLabel]);

    const consumerTotals = useMemo(() => aggregateQueriesPerConsumer(chartData), [chartData]);

    const uniqueConsumers = useMemo(() => getUniqueConsumers(chartData), [chartData]);
    const colorScaleConfig = useMemo(() => createColorScaleConfig(uniqueConsumers), [uniqueConsumers]);

    return (
        <Flex vertical gap="large">
            {isLoadingState && !hasUsageData ? (
                <Flex vertical align="center" justify="center">
                    <Spin size="large" />
                </Flex>
            ) : !isLoadingState && !hasUsageData ? (
                <Flex vertical align="center" justify="center">
                    <Empty description={t('No usage data available for this dataset')} />
                </Flex>
            ) : (
                <Row gutter={[32, 32]}>
                    <Col span={24}>
                        <Flex wrap gap="middle">
                            <Flex gap="large">
                                <Typography.Text>{t('Time Range')}:</Typography.Text>
                                <Radio.Group
                                    value={dayRange}
                                    onChange={(e: RadioChangeEvent) => setDayRange(e.target.value)}
                                    options={[
                                        { label: t('Last 30 days'), value: 30 },
                                        { label: t('Last 90 days'), value: 90 },
                                        { label: t('Last year'), value: longestDayRange },
                                    ]}
                                />
                            </Flex>
                        </Flex>
                    </Col>
                    <Col span={12}>
                        <QueriesOverTimeChart
                            data={chartData}
                            isLoading={isLoadingState}
                            hasData={hasUsageData}
                            colorScaleConfig={colorScaleConfig}
                        />
                    </Col>
                    <Col span={12}>
                        <QueriesPerConsumerChart
                            data={consumerTotals}
                            isLoading={isLoadingState}
                            hasData={hasUsageData}
                            colorScaleConfig={colorScaleConfig}
                        />
                    </Col>
                </Row>
            )}
            <CuratedQueriesList
                queries={curatedQueries?.dataset_curated_queries}
                isLoading={areCuratedQueriesLoading}
            />
        </Flex>
    );
}
