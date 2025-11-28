import { Area } from '@ant-design/charts';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { ChartCard } from './chart-card';
import type { ChartDataPoint } from './chart-data.utils';

type QueriesOverTimeChartProps = {
    data: ChartDataPoint[];
    isLoading: boolean;
    hasData: boolean;
    className?: string;
};

export function QueriesOverTimeChart({ data, isLoading, hasData, className }: QueriesOverTimeChartProps) {
    const { t } = useTranslation();

    const config = useMemo(() => {
        return {
            data,
            xField: 'date',
            yField: 'queryCount',
            seriesField: 'consumer',
            colorField: 'consumer',
            smooth: true,
            isStack: true,
            stack: true,
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
            },
            yAxis: {
                title: {
                    text: t('Query Count'),
                },
            },
            tooltip: {
                formatter: (datum: ChartDataPoint) => ({
                    name: datum.consumer,
                    value: datum.queryCount,
                    title: datum.date,
                }),
            },
            legend: {
                position: 'top-right' as const,
            },
        };
    }, [data, t]);

    return (
        <ChartCard
            className={className}
            title={t('Usage Statistics - Last Month')}
            isLoading={isLoading}
            hasData={hasData}
            emptyDescription={t('No usage data available for the last month')}
        >
            <Area {...config} />
        </ChartCard>
    );
}
