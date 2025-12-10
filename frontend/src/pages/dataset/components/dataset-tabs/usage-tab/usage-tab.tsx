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
    transformDataForChart,
} from './components/chart-data.utils';
import { CuratedQueriesList } from './components/curated-queries-list';
import { QueriesOverTimeChart } from './components/queries-over-time-chart';
import { QueriesPerConsumerChart } from './components/queries-per-consumer-chart';

const { Link } = Typography;

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
    const yearDayRange = 365;
    const [dayRange, setDayRange] = useState<number>(yearDayRange);
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
    const hasCuratedQueries = Boolean(!areCuratedQueriesLoading && curatedQueries?.dataset_curated_queries?.length);
    const hasAnyData = hasUsageData || hasCuratedQueries;
    const unknownLabel = t('Unknown');

    const chartData = useMemo(() => {
        if (!responses?.length) {
            return [];
        }
        return transformDataForChart(responses, granularity, unknownLabel);
    }, [responses, granularity, unknownLabel]);

    const consumerTotals = useMemo(() => aggregateQueriesPerConsumer(chartData), [chartData]);

    // Use the sorted order from consumerTotals (which is already sorted by total queries descending)
    // This ensures areas with highest total queries are at the bottom of the stacked chart
    // Note: Data is now sorted by consumer total queries in the backend
    const uniqueConsumers = useMemo(() => consumerTotals.map((ct) => ct.consumer), [consumerTotals]);
    const colorScaleConfig = useMemo(() => createColorScaleConfig(uniqueConsumers), [uniqueConsumers]);

    return (
        <Flex vertical gap="large">
            {isLoadingState && !hasUsageData ? (
                <Flex vertical align="center" justify="center">
                    <Spin size="large" />
                </Flex>
            ) : !isLoadingState && !hasAnyData ? (
                <Flex vertical align="center" justify="center">
                    <Empty
                        description={
                            <Typography.Text type="secondary">
                                {t('Learn how to set up usage data ingestion in our')}{' '}
                                <Link
                                    href="https://docs.dataproductportal.com/docs/developer-guide/data-product-usage-ingestion"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    {t('documentation')}
                                </Link>
                                .
                            </Typography.Text>
                        }
                    />
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
                                        { label: t('Last year'), value: yearDayRange },
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
            {hasAnyData && (
                <CuratedQueriesList
                    queries={curatedQueries?.dataset_curated_queries}
                    isLoading={areCuratedQueriesLoading}
                />
            )}
        </Flex>
    );
}
