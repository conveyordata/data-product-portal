import { format, subDays, subMonths, subYears } from 'date-fns';

import type {
    DatasetQueryStatsDailyResponse,
    DatasetQueryStatsDailyResponses,
} from '@/types/dataset/dataset-query-stats-daily.contract';

export type TimeRange = '1m' | '90d' | '1y';
export type Granularity = 'day' | 'week' | 'month';

export type ChartDataPoint = {
    date: string; // ISO string used for x axis sorting
    displayDate: string; // human-friendly label
    timestamp: number;
    queryCount: number;
    consumer: string;
};

export type ConsumerTotal = {
    consumer: string;
    totalQueries: number;
};

export function getRangeStart(now: Date, timeRange: TimeRange): Date {
    if (timeRange === '90d') {
        return subDays(now, 90);
    }

    if (timeRange === '1y') {
        return subYears(now, 1);
    }

    return subMonths(now, 1);
}

function normalizeToUTCDate(date: Date): Date {
    return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
}

function alignToGranularity(date: Date, granularity: Granularity): Date {
    const aligned = normalizeToUTCDate(date);
    if (granularity === 'week') {
        const day = aligned.getUTCDay();
        const diff = (day + 6) % 7; // convert Sunday=0 to Monday=0
        aligned.setUTCDate(aligned.getUTCDate() - diff);
        return aligned;
    }

    if (granularity === 'month') {
        aligned.setUTCDate(1);
        return aligned;
    }

    return aligned;
}

function incrementDate(current: Date, granularity: Granularity): Date {
    const next = new Date(current);
    if (granularity === 'week') {
        next.setUTCDate(next.getUTCDate() + 7);
        return next;
    }
    if (granularity === 'month') {
        // force day 1 to avoid month rollover
        next.setUTCMonth(next.getUTCMonth() + 1, 1);
        return next;
    }
    next.setUTCDate(next.getUTCDate() + 1);
    return next;
}

function buildBuckets(rangeStart: Date, now: Date, granularity: Granularity) {
    const buckets: Array<{ isoDate: string; displayDate: string; timestamp: number }> = [];
    const start = alignToGranularity(rangeStart, granularity);
    const end = alignToGranularity(now, granularity);

    let current = new Date(start);
    let lastMonth = -1;

    while (current <= end) {
        let displayDate: string;
        if (granularity === 'day') {
            const currentMonth = current.getMonth();
            displayDate = currentMonth !== lastMonth ? format(current, 'MMM d') : format(current, 'd');
            lastMonth = currentMonth;
        } else if (granularity === 'week') {
            displayDate = format(current, 'MMM d');
        } else {
            displayDate = format(current, 'MMM');
        }

        buckets.push({
            isoDate: current.toISOString().slice(0, 10),
            displayDate,
            timestamp: current.getTime(),
        });

        current = incrementDate(current, granularity);
    }

    return buckets;
}

export function transformDataForChart(
    responses: DatasetQueryStatsDailyResponse[],
    timeRange: TimeRange,
    granularity: Granularity,
): ChartDataPoint[] {
    const now = new Date();
    const rangeStart = getRangeStart(now, timeRange);

    // transform date strings to Date objects
    const processedData = responses
        .map((stat) => {
            const date = new Date(stat.date);
            return {
                isoDate: date.toISOString().slice(0, 10),
                timestamp: date.getTime(),
                queryCount: stat.query_count,
                consumer: stat.consumer_data_product_name || 'Unknown',
            };
        })
        .sort((a, b) => a.timestamp - b.timestamp);

    const consumers = [...new Set(processedData.map((d) => d.consumer))];
    const buckets = buildBuckets(rangeStart, now, granularity);
    const dataByKey = new Map<string, number>();

    for (const entry of processedData) {
        const key = `${entry.isoDate}|${entry.consumer}`;
        const prev = dataByKey.get(key) ?? 0;
        dataByKey.set(key, prev + entry.queryCount);
    }

    const filledData: ChartDataPoint[] = [];
    for (const consumer of consumers) {
        for (const bucket of buckets) {
            const key = `${bucket.isoDate}|${consumer}`;
            filledData.push({
                date: bucket.isoDate,
                displayDate: bucket.displayDate,
                timestamp: bucket.timestamp,
                queryCount: dataByKey.get(key) ?? 0,
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

export type UsageChartProps = {
    data: DatasetQueryStatsDailyResponses | undefined;
    granularity: Granularity;
    isLoading: boolean;
    timeRange: TimeRange;
    className?: string;
};
