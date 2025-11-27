import { Area } from '@ant-design/charts';
import { Card, Empty, Spin } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import type { UsageChartProps } from './chart-data.utils';
import { transformDataForChart } from './chart-data.utils';

export function QueriesOverTimeChart({ data, granularity, isLoading, dayRange, className }: UsageChartProps) {
    const { t } = useTranslation();

    const chartData = useMemo(() => {
        if (!data?.dataset_query_stats_daily_responses) {
            return [];
        }
        return transformDataForChart(data.dataset_query_stats_daily_responses, dayRange, granularity);
    }, [data, granularity, dayRange]);

    if (isLoading) {
        return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', marginTop: '50px' }} />;
    }

    if (!data?.dataset_query_stats_daily_responses || data.dataset_query_stats_daily_responses.length === 0) {
        return <Empty description={t('No usage data available for this time range and granularity')} />;
    }

    // for options see: https://ant-design-charts.antgroup.com/options/plots/axis
    const config = {
        data: chartData,
        xField: 'date',
        yField: 'queryCount',
        seriesField: 'consumer',
        colorField: 'consumer',
        smooth: true,
        isStack: true,
        stack: true,
        shapeField: 'smooth',
        animation: {
            appear: {
                animation: 'path-in',
                duration: 1000,
            },
        },
        legend: {
            position: 'top-right' as const,
        },
        axis: {
            x: {
                title: 'Date',
                labelFontSize: 13,
            },
            y: {
                title: 'Query Count',
                labelFontSize: 13,
            },
        },
    };

    return (
        <Card className={className} title={t('Queries Over Time')} styles={{ body: { padding: 0 } }}>
            <Area {...config} />
        </Card>
    );
}
