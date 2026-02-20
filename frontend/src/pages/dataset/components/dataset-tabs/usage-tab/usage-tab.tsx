import { Alert, Col, Flex, Radio, type RadioChangeEvent, Row, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import {
    QueryStatsGranularity,
    useGetOutputPortCuratedQueriesQuery,
    useGetOutputPortQueryStatsQuery,
} from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import {
    aggregateQueriesPerConsumer,
    createColorScaleConfig,
    transformDataForChart,
} from './components/chart-data.utils';
import { CuratedQueriesList } from './components/curated-queries-list';
import { QueriesOverTimeChart } from './components/queries-over-time-chart';
import { QueriesPerConsumerChart } from './components/queries-per-consumer-chart';

type Props = {
    outputPortId: string;
    dataProductId: string;
};

function getGranularityFromDayRange(dayRange: number): QueryStatsGranularity {
    if (dayRange === 365) {
        return QueryStatsGranularity.Month;
    }
    if (dayRange === 90) {
        return QueryStatsGranularity.Week;
    }
    return QueryStatsGranularity.Day;
}

export function UsageTab({ outputPortId, dataProductId }: Props) {
    const { t } = useTranslation();
    const yearDayRange = 365;
    const [dayRange, setDayRange] = useState<number>(yearDayRange);
    const granularity = useMemo(() => getGranularityFromDayRange(dayRange), [dayRange]);

    const {
        data: { output_port_query_stats_responses: responses = [] } = {},
        isLoading,
        isFetching,
    } = useGetOutputPortQueryStatsQuery({
        dataProductId,
        id: outputPortId,
        granularity,
        dayRange,
    });

    const { data: { output_port_curated_queries: curatedQueries = [] } = {}, isLoading: areCuratedQueriesLoading } =
        useGetOutputPortCuratedQueriesQuery({ id: outputPortId, dataProductId });

    const isLoadingState = isLoading || isFetching;
    const hasUsageData = Boolean(responses.length);
    const hasCuratedQueries = Boolean(!areCuratedQueriesLoading && curatedQueries?.length);
    const unknownLabel = t('Unknown');

    const chartData = useMemo(() => {
        if (!responses.length) {
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
        <Row gutter={[32, 32]}>
            <Col span={24}>
                <Flex justify={'center'}>
                    <Radio.Group
                        optionType="button"
                        value={dayRange}
                        onChange={(e: RadioChangeEvent) => setDayRange(e.target.value)}
                        options={[
                            { label: t('Last 30 days'), value: 30 },
                            { label: t('Last 90 days'), value: 90 },
                            { label: t('Last year'), value: yearDayRange },
                        ]}
                    />
                </Flex>
            </Col>

            {!hasUsageData && !hasCuratedQueries && (
                <Col span={24}>
                    <Alert
                        title={
                            <Trans t={t}>
                                No usage data available. Learn how to set up usage data ingestion in our{' '}
                                <Typography.Link
                                    href="https://docs.dataproductportal.com/docs/developer-guide/data-product-usage-ingestion"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    documentation
                                </Typography.Link>
                                .
                            </Trans>
                        }
                        type="info"
                        showIcon
                    />
                </Col>
            )}
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
            <Col span={24}>
                <CuratedQueriesList queries={curatedQueries} isLoading={areCuratedQueriesLoading} />
            </Col>
        </Row>
    );
}
