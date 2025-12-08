import { addDays, format, isSameDay, isSameMonth, subMonths } from 'date-fns';

import type { DatasetQueryStatsDailyResponse } from '@/types/dataset/dataset-query-stats-daily.contract';

export type ChartDataPoint = {
    date: string;
    timestamp: number;
    queryCount: number;
    consumer: string;
};

export function transformDataForChart(
    responses: DatasetQueryStatsDailyResponse[],
    unknownLabel: string,
): ChartDataPoint[] {
    const oneMonthAgo = subMonths(new Date(), 1);
    const now = new Date();

    const processedData = responses
        .map((stat) => {
            const date = new Date(stat.date);
            return {
                timestamp: date.getTime(),
                queryCount: stat.query_count,
                consumer: stat.consumer_data_product_name || unknownLabel,
            };
        })
        .filter((stat) => stat.timestamp >= oneMonthAgo.getTime())
        .sort((a, b) => a.timestamp - b.timestamp);

    const consumers = [...new Set(processedData.map((d) => d.consumer))];

    const allDates: Array<{ date: string; timestamp: number }> = [];
    let currentDate = new Date(oneMonthAgo);
    let lastMonthDate: Date | null = null;
    while (currentDate <= now) {
        const dateLabel =
            !lastMonthDate || !isSameMonth(currentDate, lastMonthDate)
                ? format(currentDate, 'MMM d')
                : format(currentDate, 'd');
        lastMonthDate = currentDate;

        allDates.push({
            date: dateLabel,
            timestamp: currentDate.getTime(),
        });
        currentDate = addDays(currentDate, 1);
    }

    const filledData: ChartDataPoint[] = [];
    for (const consumer of consumers) {
        for (const dateInfo of allDates) {
            const existingData = processedData.find(
                (d) => isSameDay(d.timestamp, dateInfo.timestamp) && d.consumer === consumer,
            );
            filledData.push({
                date: dateInfo.date,
                timestamp: dateInfo.timestamp,
                queryCount: existingData?.queryCount || 0,
                consumer: consumer,
            });
        }
    }

    return filledData.sort((a, b) => a.timestamp - b.timestamp);
}
