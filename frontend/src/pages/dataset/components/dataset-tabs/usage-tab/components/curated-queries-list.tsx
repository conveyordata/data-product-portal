import { Card, Empty, List } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { OutputPortCuratedQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { CuratedQueryItem, SQL_LINES_THRESHOLD } from './curated-query-item';

type CuratedQueriesListProps = {
    queries?: OutputPortCuratedQuery[];
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
        <Card title={t('Curated queries')}>
            <List
                loading={isLoading}
                itemLayout="vertical"
                dataSource={queriesList}
                // split={false}
                locale={{ emptyText: <Empty description={t('No curated queries available')} /> }}
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
