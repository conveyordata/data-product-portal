import { Area } from '@ant-design/charts';
import { Card, Empty, Spin } from 'antd';
import { format } from 'date-fns';
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

    const config = {
        data: chartData,
        xField: 'date',
        yField: 'queryCount',
        seriesField: 'consumer',
        colorField: 'consumer',
        smooth: true,
        isStack: true,
        stack: true,
        // shapeField: 'smooth',
        animation: {
            appear: {
                animation: 'path-in',
                duration: 1000,
            },
        },
        xAxis: {
            title: {
                text: t('Date'),
            },
            label: {
                formatter: (value: string) => {
                    const dateValue = new Date(value);
                    if (Number.isNaN(dateValue.getTime())) {
                        return value;
                    }

                    if (granularity === 'day') {
                        const isShortRange = dayRange <= 31;
                        if (isShortRange) {
                            return dateValue.getDate() === 1 ? format(dateValue, 'MMM d') : format(dateValue, 'd');
                        }
                        return dateValue.getDate() === 1 ? format(dateValue, 'MMM') : '';
                    }

                    if (granularity === 'week') {
                        return format(dateValue, 'MMM d');
                    }

                    return format(dateValue, 'MMM');
                },
            },
        },
        yAxis: {
            title: {
                text: t('Query Count'),
            },
        },
        legend: {
            position: 'top-right' as const,
        },
    };

    return (
        <Card className={className} title={t('Queries Over Time')} styles={{ body: { padding: 0 } }}>
            <Area {...config} />
        </Card>
    );
}
