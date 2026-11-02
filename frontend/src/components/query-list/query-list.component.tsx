import type { ComponentProps, ReactNode } from 'react';
import {
    EmptyState,
    type EmptyStateFilter,
    type EmptyStateQuery,
    emptyStateQueryProps,
    hasFailed,
    isAwaitingData,
} from '@/components/empty-state/empty-state.component.tsx';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';

type Props<T> = {
    query: EmptyStateQuery;
    items: T[];
    renderItem: (item: T) => ReactNode;
    /** Plural noun for the items, used in the no-match and failed-load messages. */
    subject: string;
    emptyState: Pick<ComponentProps<typeof EmptyState>, 'icon' | 'title' | 'description' | 'action' | 'size'>;
    filter?: EmptyStateFilter;
};

/** The ListTable counterpart for lists rendered as cards: spinner, items, or the empty state. */
export function QueryList<T>({ query, items, renderItem, subject, emptyState, filter }: Props<T>) {
    if (isAwaitingData(query)) return <LoadingSpinner />;

    const visibleItems = hasFailed(query) ? [] : items;
    if (visibleItems.length > 0) return <>{visibleItems.map(renderItem)}</>;

    return <EmptyState {...emptyState} subject={subject} filter={filter} {...emptyStateQueryProps(query)} />;
}
