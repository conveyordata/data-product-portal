import { CopyOutlined } from '@ant-design/icons';
import { Button, Flex, List, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { magula } from 'react-syntax-highlighter/dist/esm/styles/hljs';

import type { DatasetCuratedQueryContract } from '@/types/dataset';
import styles from './curated-query-item.module.scss';

export const SQL_LINES_THRESHOLD = 10;

type CuratedQueryItemProps = {
    query: DatasetCuratedQueryContract;
    isExpanded: boolean;
    onToggle: () => void;
    onCopy: (text: string) => void;
};

export function CuratedQueryItem({ query, isExpanded, onToggle, onCopy }: CuratedQueryItemProps) {
    const { t } = useTranslation();
    const hasLongSql = query.query_text.split('\n').length > SQL_LINES_THRESHOLD;
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
