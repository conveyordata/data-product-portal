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

    // for options see: https://ant-design-charts.antgroup.com/options/plots/axis
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
            axis: {
                x: {
                    title: t('Date'),
                    labelFontSize: 13,
                },
                y: {
                    title: t('Query Count'),
                    labelFontSize: 13,
                },
            },
            legend: {
                position: 'top-right' as const,
            },
        };
    }, [data, t]);

    return (
        <ChartCard
            className={className}
            title={t('Queries Over Time')}
            isLoading={isLoading}
            hasData={hasData}
            emptyDescription={t('No usage data available for this time range and granularity')}
        >
            <Area {...config} />
        </ChartCard>
    );
}
