import { Area } from '@ant-design/charts';
import { CopyOutlined } from '@ant-design/icons';
import { Button, Card, Empty, Flex, List, message, Skeleton, Typography } from 'antd';
import { addDays, format, isSameDay, isSameMonth, subMonths } from 'date-fns';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { magula } from 'react-syntax-highlighter/dist/esm/styles/hljs';

import type { DatasetCuratedQueryContract } from '@/types/dataset';
import type {
    DatasetQueryStatsDailyResponse,
    DatasetQueryStatsDailyResponses,
} from '@/types/dataset/dataset-query-stats-daily.contract';
import styles from './usage-chart.module.scss';

const LINES_THRESHOLD = 10;

type ChartDataPoint = {
    date: string;
    timestamp: number;
    queryCount: number;
    consumer: string;
};

type CuratedQueryItemProps = {
    query: DatasetCuratedQueryContract;
    isExpanded: boolean;
    onToggle: () => void;
    onCopy: (text: string) => void;
};

type Props = {
    usageData?: DatasetQueryStatsDailyResponses;
    curatedQueries?: DatasetCuratedQueryContract[];
    isUsageLoading: boolean;
    areCuratedQueriesLoading: boolean;
};

function CuratedQueryItem({ query, isExpanded, onToggle, onCopy }: CuratedQueryItemProps) {
    const { t } = useTranslation();
    const hasLongSql = query.query_text.split('\n').length > LINES_THRESHOLD;
    const shouldShowToggle = hasLongSql;

    return (
        <List.Item>
            <Flex vertical gap={12}>
                <Flex vertical gap={4}>
                    <Typography.Text strong>{query.title}</Typography.Text>
                    {query.description && <Typography.Text type="secondary">{query.description}</Typography.Text>}
                </Flex>
                <Flex vertical gap={4}>
                    <Flex gap={8} align="start">
                        <Flex flex={1} className={`${styles.sqlCode} ${isExpanded ? styles.sqlCodeExpanded : ''}`}>
                            <SyntaxHighlighter
                                language="sql"
                                style={magula}
                                className={styles.syntaxHighlighter}
                                showLineNumbers={false}
                            >
                                {query.query_text}
                            </SyntaxHighlighter>
                        </Flex>
                        <Button
                            type="default"
                            size="middle"
                            icon={<CopyOutlined />}
                            aria-label={t('Copy SQL')}
                            onClick={() => onCopy(query.query_text)}
                        />
                    </Flex>
                    {shouldShowToggle && (
                        <Button type="link" size="small" onClick={onToggle}>
                            {isExpanded ? t('Show less') : t('Show more')}
                        </Button>
                    )}
                </Flex>
            </Flex>
        </List.Item>
    );
}

function transformDataForChart(responses: DatasetQueryStatsDailyResponse[], unknownLabel: string): ChartDataPoint[] {
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

export function UsageChart({
    usageData,
    curatedQueries,
    isUsageLoading,
    areCuratedQueriesLoading,
}: Props) {
    const { t } = useTranslation();
    const [expandedQueries, setExpandedQueries] = useState<Record<string, boolean>>({});
    const [messageApi, contextHolder] = message.useMessage();

    const chartData = useMemo(() => {
        if (!usageData?.dataset_query_stats_daily_responses) {
            return [];
        }
        return transformDataForChart(usageData.dataset_query_stats_daily_responses, t('Unknown'));
    }, [usageData, t]);

    const queries = useMemo(() => curatedQueries ?? [], [curatedQueries]);

    const handleToggle = (id: string) => {
        setExpandedQueries((prev) => ({ ...prev, [id]: !prev[id] }));
    };

    const handleCopy = async (queryText: string) => {
        try {
            await navigator.clipboard.writeText(queryText);
            messageApi.success(t('SQL copied to clipboard'));
        } catch (_error) {
            messageApi.error(t('Failed to copy SQL'));
        }
    };

    const getIsExpanded = (id: string, queryText: string) => {
        if (id in expandedQueries) {
            return expandedQueries[id];
        }
        return queryText.split('\n').length <= LINES_THRESHOLD;
    };

    const hasUsageData =
        usageData?.dataset_query_stats_daily_responses &&
        usageData.dataset_query_stats_daily_responses.length > 0;

    const chartConfig = {
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
            formatter: (datum: ChartDataPoint) => ({
                name: datum.consumer,
                value: datum.queryCount,
                title: datum.date,
            }),
        },
        legend: {
            position: 'top-right' as const,
        },
    };

    return (
        <Flex vertical gap={24}>
            {contextHolder}
            <Card bordered={false}>
                {isUsageLoading ? (
                    <LoadingSpinner />
                ) : !hasUsageData ? (
                    <Empty description={t('No usage data available for the last month')} />
                ) : (
                    <Flex vertical gap={16}>
                        <Typography.Title level={3}>{t('Usage Statistics - Last Month')}</Typography.Title>
                        <Area {...chartConfig} />
                    </Flex>
                )}
            </Card>
            <Card title={t('Curated Queries')} bordered={false}>
                {areCuratedQueriesLoading ? (
                    <Skeleton active paragraph={{ rows: 4 }} />
                ) : queries.length === 0 ? (
                    <Empty description={t('No curated queries available')} />
                ) : (
                    <List
                        itemLayout="vertical"
                        dataSource={queries}
                        renderItem={(item) => {
                            const key = item.curated_query_id;
                            const isExpanded = getIsExpanded(key, item.query_text);

                            return (
                                <CuratedQueryItem
                                    key={key}
                                    query={item}
                                    isExpanded={isExpanded}
                                    onToggle={() => handleToggle(key)}
                                    onCopy={handleCopy}
                                />
                            );
                        }}
                    />
                )}
            </Card>
        </Flex>
    );
}
