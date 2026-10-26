import { ConsoleSqlOutlined } from '@ant-design/icons';
import { Card, List } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
    EmptyState,
    type EmptyStateQuery,
    emptyStateQueryProps,
    hasFailed,
    isAwaitingData,
} from '@/components/empty-state/empty-state.component.tsx';
import type { OutputPortCuratedQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { dispatchMessage } from '@/utils/feedback.ts';
import { CuratedQueryItem, SQL_LINES_THRESHOLD } from './curated-query-item';

type CuratedQueriesListProps = {
    queries?: OutputPortCuratedQuery[];
    query: EmptyStateQuery;
};

export function CuratedQueriesList({ queries, query }: CuratedQueriesListProps) {
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
        <Card title={t('Curated queries')}>
            <List
                loading={isAwaitingData(query)}
                itemLayout="vertical"
                dataSource={hasFailed(query) ? [] : queriesList}
                locale={{
                    emptyText: (
                        <EmptyState
                            size="small"
                            icon={<ConsoleSqlOutlined />}
                            title={t('No curated queries yet')}
                            description={t('Owners can publish example queries here to help you get started.')}
                            {...emptyStateQueryProps(query)}
                        />
                    ),
                }}
                bordered={false}
                renderItem={(item) => {
                    const key = `${item.output_port_id}-${item.sort_order}`;
                    const isExpanded =
                        expandedQueries[key] ?? item.query_text.split('\n').length <= SQL_LINES_THRESHOLD;

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
        </Card>
    );
}
