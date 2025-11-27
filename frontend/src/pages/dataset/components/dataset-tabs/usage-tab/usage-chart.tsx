import { Area } from '@ant-design/charts';
import { Empty, Flex, Typography } from 'antd';
import { addDays, format, isSameDay, isSameMonth, subMonths } from 'date-fns';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import type {
    DatasetQueryStatsDailyResponse,
    DatasetQueryStatsDailyResponses,
} from '@/types/dataset/dataset-query-stats-daily.contract';

type Props = {
    data: DatasetQueryStatsDailyResponses | undefined;
    isLoading: boolean;
};

type ChartDataPoint = {
    date: string;
    timestamp: number;
    queryCount: number;
    consumer: string;
};

function transformDataForChart(responses: DatasetQueryStatsDailyResponse[], unknownLabel: string): ChartDataPoint[] {
    const oneMonthAgo = subMonths(new Date(), 1);
    const now = new Date();

    // transform date strings to Date objects
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

    // Get unique consumers
    const consumers = [...new Set(processedData.map((d) => d.consumer))];

    // Create a list of all dates in the range formatted as 'MMM d' or 'd'
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

    // For each consumer and each date, add data point (with [] if missing)
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

export function UsageChart({ data, isLoading }: Props) {
    const { t } = useTranslation();

    const chartData = useMemo(() => {
        if (!data?.dataset_query_stats_daily_responses) {
            return [];
        }
        return transformDataForChart(data.dataset_query_stats_daily_responses, t('Unknown'));
    }, [data, t]);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    if (!data?.dataset_query_stats_daily_responses || data.dataset_query_stats_daily_responses.length === 0) {
        return <Empty description={t('No usage data available for the last month')} />;
    }

    const config = {
        data: chartData,
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
        xAxis: {
            title: {
                text: t('Date'),
            },
        },
        yAxis: {
            title: {
                text: t('Query Count'),
            },
        },
        tooltip: {
            formatter: (datum: ChartDataPoint) => {
                return {
                    name: datum.consumer,
                    value: datum.queryCount,
                    title: datum.date,
                };
            },
        },
        legend: {
            position: 'top-right' as const,
        },
    };

    return (
        <Flex vertical>
            <Typography.Title level={3}>{t('Usage Statistics - Last Month')}</Typography.Title>
            <Area {...config} />
        </Flex>
    );
}
