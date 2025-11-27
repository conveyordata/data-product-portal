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

import type {
    DatasetQueryStatsDailyResponse,
    DatasetQueryStatsDailyResponses,
} from '@/types/dataset/dataset-query-stats-daily.contract';

export type DayRange = number;
export type Granularity = 'day' | 'week' | 'month';

export type ChartDataPoint = {
    date: string; // ISO string used for x axis sorting
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
            displayDate = `week:${format(current, 'ww')}`;
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
): ChartDataPoint[] {
    const now = new Date();
    const rangeStart = getRangeStart(now, dayRange);

    // transform date strings to Date objects
    const processedData = responses
        .map((stat) => {
            const date = parseISO(stat.date);
            return {
                isoDate: formatISO(date, { representation: 'date' }),
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
                date: bucket.displayDate,
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
    dayRange: DayRange;
    className?: string;
};
