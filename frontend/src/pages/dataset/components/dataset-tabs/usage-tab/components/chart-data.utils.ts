import { format, parseISO } from 'date-fns';

import type { DatasetQueryStatsDailyResponse } from '@/types/dataset/dataset-query-stats-daily.contract';

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
    responses: DatasetQueryStatsDailyResponse[],
    granularity: Granularity,
    unknownLabel: string,
): ChartDataPoint[] {
    // Backend already builds buckets and fills missing periods with 0
    // We just need to format the data for the chart
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

    // Sort by timestamp to ensure correct chronological order
    // (backend sorts, but this ensures frontend consistency)
    return chartData.sort((a, b) => a.timestamp - b.timestamp);
}

export function aggregateQueriesPerConsumer(dataPoints: ChartDataPoint[]): ConsumerTotal[] {
    const totalsMap = new Map<string, number>();

    for (const point of dataPoints) {
        const current = totalsMap.get(point.consumer) ?? 0;
        totalsMap.set(point.consumer, current + point.queryCount);
    }

    return [...totalsMap.entries()]
        .map(([consumer, totalQueries]) => ({
            consumer,
            totalQueries,
        }))
        .sort((a, b) => b.totalQueries - a.totalQueries);
}
