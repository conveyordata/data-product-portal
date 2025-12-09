import { Area } from '@ant-design/charts';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { ChartCard } from './chart-card';
import type { ChartDataPoint, ColorScaleConfig } from './chart-data.utils';

type QueriesOverTimeChartProps = {
    data: ChartDataPoint[];
    isLoading: boolean;
    hasData: boolean;
    colorScaleConfig: ColorScaleConfig;
};

export function QueriesOverTimeChart({ data, isLoading, hasData, colorScaleConfig }: QueriesOverTimeChartProps) {
    const { t } = useTranslation();

    const config = useMemo(() => {
        return {
            data,
            xField: 'date',
            yField: 'queryCount',
            seriesField: 'consumer',
            colorField: 'consumer',
            smooth: true,
            stack: true,
            ...colorScaleConfig,
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
    }, [data, t, colorScaleConfig]);

    return (
        <ChartCard
            title={t('Usage Statistics - Last Month')}
            isLoading={isLoading}
            hasData={hasData}
            emptyDescription={t('No usage data available for the last month')}
        >
            <Area {...config} />
        </ChartCard>
    );
}
