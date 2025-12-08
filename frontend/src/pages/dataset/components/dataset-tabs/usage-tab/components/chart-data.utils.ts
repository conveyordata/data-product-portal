import {
    addDays,
    addMonths,
    addWeeks,
    format,
    formatISO,
    parseISO,
    startOfDay,
    startOfMonth,
    startOfWeek,
    subDays,
} from 'date-fns';

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

export function getRangeStart(now: Date, dayRange: DayRange): Date {
    const safeRange = Math.max(dayRange, 1);
    return subDays(now, safeRange);
}

function alignToGranularity(date: Date, granularity: Granularity): Date {
    if (granularity === 'week') {
        return startOfWeek(date, { weekStartsOn: 1 });
    }
    if (granularity === 'month') {
        return startOfMonth(date);
    }
    return startOfDay(date);
}

function incrementDate(current: Date, granularity: Granularity): Date {
    if (granularity === 'week') {
        return addWeeks(current, 1);
    }
    if (granularity === 'month') {
        return addMonths(current, 1);
    }
    return addDays(current, 1);
}

function buildBuckets(rangeStart: Date, now: Date, granularity: Granularity) {
    const buckets: Array<{ isoDate: string; displayDate: string; timestamp: number }> = [];
    const start = alignToGranularity(rangeStart, granularity);
    const end = alignToGranularity(now, granularity);

    let current = new Date(start);

    while (current <= end) {
        let displayDate: string;
        if (granularity === 'month') {
            displayDate = format(current, 'MMM-yyyy');
        } else if (granularity === 'week') {
            displayDate = `${format(current, 'yyyy')}-W${format(current, 'II')}`;
        } else {
            displayDate = format(current, 'dd-MM-yyyy');
        }

        buckets.push({
            isoDate: formatISO(current, { representation: 'date' }),
            displayDate,
            timestamp: current.getTime(),
        });

        current = incrementDate(current, granularity);
    }

    return buckets;
}

export function transformDataForChart(
    responses: DatasetQueryStatsDailyResponse[],
    dayRange: DayRange,
    granularity: Granularity,
    unknownLabel: string,
): ChartDataPoint[] {
    const now = new Date();
    const rangeStart = getRangeStart(now, dayRange);

    // Backend already aggregates by granularity, so we just map responses to buckets
    // Create a map of backend data: key = "isoDate|consumer"
    const backendDataMap = new Map<string, number>();
    const consumers = new Set<string>();

    for (const stat of responses) {
        const date = parseISO(stat.date);
        const isoDate = formatISO(date, { representation: 'date' });
        const consumer = stat.consumer_data_product_name || unknownLabel;
        const key = `${isoDate}|${consumer}`;

        // Backend already aggregated, so there should only be one entry per key
        backendDataMap.set(key, stat.query_count);
        consumers.add(consumer);
    }

    // Create buckets for the full time range (to fill gaps)
    const buckets = buildBuckets(rangeStart, now, granularity);

    // Map backend data to buckets and fill missing buckets with 0
    const filledData: ChartDataPoint[] = [];
    for (const consumer of consumers) {
        for (const bucket of buckets) {
            const key = `${bucket.isoDate}|${consumer}`;
            filledData.push({
                date: bucket.displayDate,
                timestamp: bucket.timestamp,
                queryCount: backendDataMap.get(key) ?? 0,
                consumer,
            });
        }
    }

    return filledData.sort((a, b) => a.timestamp - b.timestamp);
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
