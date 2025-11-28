import { Empty, Flex, List, message, Skeleton } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import type { DatasetCuratedQueryContract } from '@/types/dataset';
import styles from './curated-queries-list.module.scss';
import { CuratedQueryItem, SQL_LINES_THRESHOLD } from './curated-query-item';

type CuratedQueriesListProps = {
    queries?: DatasetCuratedQueryContract[];
    isLoading: boolean;
};

export function CuratedQueriesList({ queries, isLoading }: CuratedQueriesListProps) {
    const { t } = useTranslation();
    const [expandedQueries, setExpandedQueries] = useState<Record<string, boolean>>({});
    const [messageApi, contextHolder] = message.useMessage();

    const queriesList = useMemo(() => queries ?? [], [queries]);

    const handleToggle = useCallback((id: string) => {
        setExpandedQueries((prev) => ({ ...prev, [id]: !prev[id] }));
    }, []);

    const handleCopy = useCallback(
        async (queryText: string) => {
            try {
                await navigator.clipboard.writeText(queryText);
                messageApi.success(t('SQL copied to clipboard'));
            } catch (_error) {
                messageApi.error(t('Failed to copy SQL'));
            }
        },
        [messageApi, t],
    );

    const getIsExpanded = useCallback(
        (id: string, queryText: string) => {
            if (id in expandedQueries) {
                return expandedQueries[id];
            }
            return queryText.split('\n').length <= SQL_LINES_THRESHOLD;
        },
        [expandedQueries],
    );

    return (
        <>
            {contextHolder}
            <Flex vertical className={styles.curatedQueriesSection}>
                {isLoading ? (
                    <Skeleton active paragraph={{ rows: 4 }} />
                ) : queriesList.length === 0 ? (
                    <Empty description={t('No curated queries available')} />
                ) : (
                    <List
                        itemLayout="vertical"
                        dataSource={queriesList}
                        split={false}
                        className={styles.curatedQueries}
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
            </Flex>
        </>
    );
}
