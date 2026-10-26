import { SearchOutlined, WarningOutlined } from '@ant-design/icons';
import { Button, Flex, Typography, theme } from 'antd';
import clsx from 'clsx';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import styles from './empty-state.module.scss';

export type EmptyStateFilter = {
    hasOtherFilters?: boolean;
    searchTerm?: string;
    onClear: () => void;
};

export type EmptyStateQuery = {
    isFetching: boolean;
    isUninitialized: boolean;
    isError: boolean;
    currentData?: unknown;
    refetch: () => unknown;
};

// A failed refetch keeps currentData, so only a failure without data for the current arguments counts.
export function hasFailed(query: EmptyStateQuery) {
    return query.isError && query.currentData === undefined;
}

// No data for the current arguments yet: first load, new arguments, or a query still waiting on its skip condition.
// A background refetch keeps the current data, so it does not count.
export function isAwaitingData(query: EmptyStateQuery) {
    return query.currentData === undefined && (query.isFetching || query.isUninitialized);
}

export function emptyStateQueryProps(query: EmptyStateQuery) {
    return { loading: isAwaitingData(query), error: hasFailed(query), onRetry: query.refetch };
}

export function searchFilter(searchTerm: string, setSearchTerm: (value: string) => unknown): EmptyStateFilter {
    return { searchTerm, onClear: () => setSearchTerm('') };
}

type Props = {
    icon: ReactNode;
    title: string;
    description?: ReactNode;
    action?: ReactNode;
    loading?: boolean;
    size?: 'default' | 'small';
} & ({ error?: false; onRetry?: () => unknown } | { error: boolean; onRetry: () => unknown }) &
    (
        | {
              /** Plural noun for what is listed, used in the no-match and failed-load messages. */
              subject: string;
              filter?: EmptyStateFilter;
          }
        | { subject?: undefined; filter?: undefined }
    );

export function EmptyState({
    icon,
    title,
    description,
    action,
    subject,
    filter,
    loading,
    error,
    onRetry,
    size = 'default',
}: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();

    if (loading) return null;

    const activeFilter = filter?.hasOtherFilters || filter?.searchTerm ? filter : undefined;

    let content = {
        icon,
        title,
        description,
        action,
        tileColors: { backgroundColor: token.colorPrimaryBg, color: token.colorPrimary },
    };
    if (error) {
        content = {
            icon: <WarningOutlined />,
            title: subject ? t("Couldn't load {{subject}}", { subject }) : t("Couldn't load this section"),
            description: undefined,
            action: <Button onClick={() => onRetry?.()}>{t('Try again')}</Button>,
            tileColors: { backgroundColor: token.colorWarningBg, color: token.colorWarning },
        };
    } else if (activeFilter) {
        const { searchTerm, hasOtherFilters, onClear } = activeFilter;
        let filteredTitle = t('No {{subject}} match the current filters', { subject });
        if (searchTerm) {
            filteredTitle = hasOtherFilters
                ? t('No {{subject}} match "{{searchTerm}}" with the current filters', { subject, searchTerm })
                : t('No {{subject}} match "{{searchTerm}}"', { subject, searchTerm });
        }
        content = {
            ...content,
            icon: <SearchOutlined />,
            title: filteredTitle,
            description: undefined,
            action: <Button onClick={onClear}>{hasOtherFilters ? t('Clear filters') : t('Clear search')}</Button>,
        };
    }

    return (
        <Flex vertical align="center" gap="small" role="status" className={clsx(styles.container, styles[size])}>
            <div className={styles.tile} style={content.tileColors} aria-hidden>
                {content.icon}
            </div>
            <Typography.Text strong style={size === 'default' ? { fontSize: token.fontSizeLG } : undefined}>
                {content.title}
            </Typography.Text>
            {content.description && (
                <Typography.Text type="secondary" className={styles.description}>
                    {content.description}
                </Typography.Text>
            )}
            {content.action}
        </Flex>
    );
}
