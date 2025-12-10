import { Bar } from '@ant-design/charts';
import { useTranslation } from 'react-i18next';

import { ChartCard } from './chart-card';
import type { ColorScaleConfig, ConsumerTotal } from './chart-data.utils';

type QueriesPerConsumerChartProps = {
    data: ConsumerTotal[];
    isLoading: boolean;
    hasData: boolean;
    colorScaleConfig: ColorScaleConfig;
};

export function QueriesPerConsumerChart({ data, isLoading, hasData, colorScaleConfig }: QueriesPerConsumerChartProps) {
    const { t } = useTranslation();

    // for options see: https://ant-design-charts.antgroup.com/options/plots/axis
    const config = {
        data,
        xField: 'consumer',
        yField: 'totalQueries',
        colorField: 'consumer',
        ...colorScaleConfig,
        coordinate: {
            actions: [['transpose']],
        },
        legend: false as const,
        axis: {
            x: {
                title: t('Consuming Data Product'),
                labelFontSize: 15,
            },
            y: {
                title: t('Query Count'),
                labelFontSize: 15,
            },
        },
    };

    return (
        <ChartCard
            title={t('Queries per Consumer')}
            isLoading={isLoading}
            hasData={hasData}
            emptyDescription={t('No usage data available for this time range and granularity')}
        >
            <Bar {...config} />
        </ChartCard>
    );
}
