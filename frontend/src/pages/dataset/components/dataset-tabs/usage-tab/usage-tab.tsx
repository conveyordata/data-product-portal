import { Flex, Select, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useGetDatasetQueryStatsDailyQuery } from '@/store/features/datasets/datasets-api-slice';
import { QueriesOverTimeChart } from './components/queries-over-time-chart';
import { QueriesPerConsumerChart } from './components/queries-per-consumer-chart';
import styles from './usage-tab.module.scss';

type Props = {
    datasetId: string;
};

export function UsageTab({ datasetId }: Props) {
    const { t } = useTranslation();
    const [granularity, setGranularity] = useState<'day' | 'week' | 'month'>('week');
    const [timeRange, setTimeRange] = useState<'1m' | '90d' | '1y'>('90d');

    const granularityOptions = useMemo(
        () => [
            { label: t('Day'), value: 'day' },
            { label: t('Week'), value: 'week' },
            { label: t('Month'), value: 'month' },
        ],
        [t],
    );

    const timeRangeOptions = useMemo(
        () => [
            { label: t('Last 30 days'), value: '1m' },
            { label: t('Last 90 days'), value: '90d' },
            { label: t('Last year'), value: '1y' },
        ],
        [t],
    );

    const { data, isLoading } = useGetDatasetQueryStatsDailyQuery({
        datasetId,
        granularity,
        timeRange,
    });

    return (
        <Flex vertical className={styles.container}>
            <Flex className={styles.filters} gap={24} wrap>
                <Flex vertical className={styles.filterGroup}>
                    <Typography.Text>{t('Granularity')}</Typography.Text>
                    <Select value={granularity} onChange={setGranularity} options={granularityOptions} />
                </Flex>
                <Flex vertical className={styles.filterGroup}>
                    <Typography.Text>{t('Time Range')}</Typography.Text>
                    <Select value={timeRange} onChange={setTimeRange} options={timeRangeOptions} />
                </Flex>
            </Flex>
            <Flex className={styles.chartsGrid} gap={16} wrap>
                <QueriesOverTimeChart
                    className={styles.chartCard}
                    data={data}
                    granularity={granularity}
                    isLoading={isLoading}
                    timeRange={timeRange}
                />
                <QueriesPerConsumerChart
                    className={styles.chartCard}
                    data={data}
                    granularity={granularity}
                    isLoading={isLoading}
                    timeRange={timeRange}
                />
            </Flex>
        </Flex>
    );
}
