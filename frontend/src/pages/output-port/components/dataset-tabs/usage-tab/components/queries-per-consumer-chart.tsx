import { Bar } from '@ant-design/charts';
import { useTranslation } from 'react-i18next';

import type { EmptyStateQuery } from '@/components/empty-state/empty-state.component.tsx';
import { ChartCard } from './chart-card';
import type { ColorScaleConfig, ConsumerTotal } from './chart-data.utils';

type QueriesPerConsumerChartProps = {
    data: ConsumerTotal[];
    query: EmptyStateQuery;
    hasData: boolean;
    colorScaleConfig: ColorScaleConfig;
};

export default function QueriesPerConsumerChart({
    data,
    query,
    hasData,
    colorScaleConfig,
}: QueriesPerConsumerChartProps) {
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
        <ChartCard title={t('Queries per Consumer')} query={query} hasData={hasData}>
            <Bar {...config} />
        </ChartCard>
    );
}
