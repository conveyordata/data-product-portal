import { Area } from '@ant-design/charts';
import { Empty, Spin } from 'antd';
import { format, subMonths } from 'date-fns';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
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

function transformDataForChart(responses: DatasetQueryStatsDailyResponse[]): ChartDataPoint[] {
    const oneMonthAgo = subMonths(new Date(), 1);
    const now = new Date();

    // transform date strings to Date objects
    const processedData = responses
        .map((stat) => {
            const date = new Date(stat.date);
            return {
                timestamp: date.getTime(),
                queryCount: stat.query_count,
                consumer: stat.consumer_data_product_name || 'Unknown',
            };
        })
        .filter((stat) => stat.timestamp >= oneMonthAgo.getTime())
        .sort((a, b) => a.timestamp - b.timestamp);

    // Get unique consumers
    const consumers = [...new Set(processedData.map((d) => d.consumer))];

    // Create a list of all dates in the range formatted as 'MMM d' or 'd'
    const allDates: Array<{ date: string; timestamp: number }> = [];
    let currentDate = new Date(oneMonthAgo);
    let lastMonth = -1;
    while (currentDate <= now) {
        const currentMonth = currentDate.getMonth();
        const dateLabel = currentMonth !== lastMonth ? format(currentDate, 'MMM d') : format(currentDate, 'd');
        lastMonth = currentMonth;

        allDates.push({
            date: dateLabel,
            timestamp: currentDate.getTime(),
        });
        currentDate = new Date(currentDate.getTime() + 24 * 60 * 60 * 1000); // Add one day
    }

    // For each consumer and each date, add data point (with [] if missing)
    const filledData: ChartDataPoint[] = [];
    for (const consumer of consumers) {
        for (const dateInfo of allDates) {
            const existingData = processedData.find((d) => {
                // Match by timestamp (same day)
                const dataDate = new Date(d.timestamp);
                const targetDate = new Date(dateInfo.timestamp);
                return dataDate.toDateString() === targetDate.toDateString() && d.consumer === consumer;
            });
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
        return transformDataForChart(data.dataset_query_stats_daily_responses);
    }, [data]);

    if (isLoading) {
        return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', marginTop: '50px' }} />;
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
        <div style={{ padding: '24px' }}>
            <h3>{t('Usage Statistics - Last Month')}</h3>
            <Area {...config} />
        </div>
    );
}
