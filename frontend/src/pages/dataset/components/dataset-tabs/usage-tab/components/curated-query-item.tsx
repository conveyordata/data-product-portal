import { CopyOutlined } from '@ant-design/icons';
import { Button, Flex, List } from 'antd';
import { useTranslation } from 'react-i18next';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import sql from 'react-syntax-highlighter/dist/esm/languages/hljs/sql';
import { magula } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import type { OutputPortCuratedQuery } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import styles from './curated-query-item.module.scss';

SyntaxHighlighter.registerLanguage('sql', sql);

export const SQL_LINES_THRESHOLD = 10;

type CuratedQueryItemProps = {
    query: OutputPortCuratedQuery;
    isExpanded: boolean;
    onToggle: () => void;
    onCopy: (text: string) => void;
};

export function CuratedQueryItem({ query, isExpanded, onToggle, onCopy }: CuratedQueryItemProps) {
    const { t } = useTranslation();
    const hasLongSql = query.query_text.split('\n').length > SQL_LINES_THRESHOLD;

    return (
        <List.Item>
            <List.Item.Meta title={query.title} description={query.description} />
            <Flex vertical gap="small">
                <Flex gap="small">
                    <Flex flex={1} className={`${styles.sqlCode} ${!isExpanded ? styles.collapsed : ''}`}>
                        <SyntaxHighlighter
                            language="sql"
                            style={magula}
                            className={styles.syntaxHighlighter}
                            showLineNumbers={false}
                            wrapLongLines={true}
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
                {hasLongSql && (
                    <Button type="link" size="small" onClick={onToggle}>
                        {isExpanded ? t('Show less') : t('Show more')}
                    </Button>
                )}
            </Flex>
        </List.Item>
    );
}
