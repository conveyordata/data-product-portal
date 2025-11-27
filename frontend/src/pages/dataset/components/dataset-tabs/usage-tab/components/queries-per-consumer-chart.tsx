import { Bar } from '@ant-design/charts';
import { Card, Empty, Spin } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import type { UsageChartProps } from './chart-data.utils';
import { aggregateQueriesPerConsumer, transformDataForChart } from './chart-data.utils';

export function QueriesPerConsumerChart({ data, granularity, isLoading, dayRange, className }: UsageChartProps) {
    const { t } = useTranslation();

    const chartData = useMemo(() => {
        if (!data?.dataset_query_stats_daily_responses) {
            return [];
        }
        return transformDataForChart(data.dataset_query_stats_daily_responses, dayRange, granularity);
    }, [data, granularity, dayRange]);

    const consumerTotals = useMemo(() => aggregateQueriesPerConsumer(chartData), [chartData]);

    if (isLoading) {
        return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', marginTop: '50px' }} />;
    }

    if (!data?.dataset_query_stats_daily_responses || data.dataset_query_stats_daily_responses.length === 0) {
        return <Empty description={t('No usage data available for this time range and granularity')} />;
    }

    const config = {
        data: consumerTotals,
        xField: 'consumer',
        yField: 'totalQueries',
        colorField: 'consumer',
        coordinate: {
            actions: [['transpose']],
        },
        legend: false as const,
        axis: {
            x: {
                title: 'Consuming Data Product',
                labelFontSize: 15,
            },
            y: {
                title: 'Query Count',
                labelFontSize: 15,
            },
        },
    };

    return (
        <Card className={className} title={t('Queries per Consumer')} styles={{ body: { padding: 0 } }}>
            <Bar {...config} />
        </Card>
    );
}
