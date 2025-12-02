import { Empty, List, Skeleton } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import type { DatasetCuratedQueryContract } from '@/types/dataset';
import { CuratedQueryItem, SQL_LINES_THRESHOLD } from './curated-query-item';

type CuratedQueriesListProps = {
    queries?: DatasetCuratedQueryContract[];
    isLoading: boolean;
};

export function CuratedQueriesList({ queries, isLoading }: CuratedQueriesListProps) {
    const { t } = useTranslation();
    const [expandedQueries, setExpandedQueries] = useState<Record<string, boolean>>({});

    const queriesList = useMemo(() => queries ?? [], [queries]);

    const handleToggle = useCallback((id: string) => {
        setExpandedQueries((prev) => ({ ...prev, [id]: !prev[id] }));
    }, []);

    const handleCopy = useCallback(
        async (queryText: string) => {
            try {
                await navigator.clipboard.writeText(queryText);
                dispatchMessage({ content: t('SQL copied to clipboard'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to copy SQL'), type: 'error' });
            }
        },
        [t],
    );

    return (
        <>
            {isLoading ? (
                <Skeleton active paragraph={{ rows: 4 }} />
            ) : queriesList.length === 0 ? (
                <Empty description={t('No curated queries available')} />
            ) : (
                <List
                    itemLayout="vertical"
                    dataSource={queriesList}
                    split={false}
                    bordered={false}
                    renderItem={(item) => {
                        const key = `${item.output_port_id}-${item.sort_order}`;
                        const queryLines = item.query_text.split('\n');
                        const hasLongSql = queryLines.length > SQL_LINES_THRESHOLD;
                        const isExpanded = expandedQueries[key] !== undefined ? expandedQueries[key] : !hasLongSql; // Short queries are expanded by default

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
        </>
    );
}
