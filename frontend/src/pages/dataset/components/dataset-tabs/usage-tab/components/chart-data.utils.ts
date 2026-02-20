import { format, parseISO } from 'date-fns';

import type { OutputPortQueryStatsResponse } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

export type DayRange = number;
export type Granularity = 'day' | 'week' | 'month';

export type ChartDataPoint = {
    date: string;
    timestamp: number;
    queryCount: number;
    consumer: string;
};

export type ConsumerTotal = {
    consumer: string;
    totalQueries: number;
};

export function transformDataForChart(
    responses: OutputPortQueryStatsResponse[],
    granularity: Granularity,
    unknownLabel: string,
): ChartDataPoint[] {
    // format the time series data for the chart
    const chartData = responses.map((stat) => {
        const date = parseISO(stat.date);
        let displayDate: string;
        if (granularity === 'month') {
            displayDate = format(date, 'MMM-yyyy');
        } else if (granularity === 'week') {
            displayDate = `${format(date, 'yyyy')}-W${format(date, 'II')}`;
        } else {
            displayDate = format(date, 'dd-MM-yyyy');
        }

        return {
            date: displayDate,
            timestamp: date.getTime(),
            queryCount: stat.query_count,
            consumer: stat.consumer_data_product_name || unknownLabel,
        };
    });

    return chartData;
}

export function aggregateQueriesPerConsumer(dataPoints: ChartDataPoint[]): ConsumerTotal[] {
    const totalsMap = new Map<string, number>();

    for (const point of dataPoints) {
        const current = totalsMap.get(point.consumer) ?? 0;
        totalsMap.set(point.consumer, current + point.queryCount);
    }

    return [...totalsMap.entries()].map(([consumer, totalQueries]) => ({
        consumer,
        totalQueries,
    }));
}

export function getUniqueConsumers(dataPoints: ChartDataPoint[]): string[] {
    const consumersSet = new Set<string>();
    for (const point of dataPoints) {
        consumersSet.add(point.consumer);
    }
    return Array.from(consumersSet).sort();
}

export function createColorScaleConfig(consumers: string[]) {
    return {
        scale: {
            color: {
                domain: consumers,
            },
        },
    };
}

export type ColorScaleConfig = ReturnType<typeof createColorScaleConfig>;
