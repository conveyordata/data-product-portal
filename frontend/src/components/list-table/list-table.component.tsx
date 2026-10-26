import { Table, type TableColumnsType, type TableProps } from 'antd';
import type { AnyObject } from 'antd/es/_util/type';
import type { FilterValue } from 'antd/es/table/interface';
import { type ComponentProps, useMemo, useState } from 'react';
import {
    EmptyState,
    type EmptyStateFilter,
    type EmptyStateQuery,
    hasFailed,
    isAwaitingData,
} from '@/components/empty-state/empty-state.component.tsx';

type FilteredInfo = Record<string, FilterValue | null>;

type Props<T> = Omit<TableProps<T>, 'dataSource' | 'columns' | 'loading' | 'locale'> & {
    query: EmptyStateQuery;
    dataSource: T[] | undefined;
    columns: TableColumnsType<T>;
    /** Plural noun for the rows, used in the no-match and failed-load messages. */
    subject: string;
    emptyState: Pick<ComponentProps<typeof EmptyState>, 'icon' | 'title' | 'description' | 'action' | 'size'>;
    filter?: EmptyStateFilter;
    /** Extra work to wait for, on top of the query's own first load. */
    loading?: boolean;
};

// Same key antd uses for a column's entry in the Table onChange filters.
function columnKey<T>(column: TableColumnsType<T>[number]) {
    if (column.key !== undefined) return String(column.key);
    const dataIndex = 'dataIndex' in column ? column.dataIndex : undefined;
    return Array.isArray(dataIndex) ? dataIndex.join('.') : String(dataIndex);
}

export function ListTable<T extends AnyObject>({
    query,
    dataSource,
    columns,
    subject,
    emptyState,
    filter,
    loading,
    onChange,
    ...tableProps
}: Props<T>) {
    const [filteredInfo, setFilteredInfo] = useState<FilteredInfo>({});
    const hasColumnFilters = Object.values(filteredInfo).some((value) => value?.length);
    const isLoading = loading || isAwaitingData(query);
    const controlledColumns = useMemo(
        () =>
            columns.map((column) =>
                'filters' in column && column.filters
                    ? { ...column, filteredValue: filteredInfo[columnKey(column)] ?? null }
                    : column,
            ),
        [columns, filteredInfo],
    );

    return (
        <Table<T>
            {...tableProps}
            dataSource={hasFailed(query) ? [] : dataSource}
            columns={controlledColumns}
            loading={isLoading}
            onChange={(pagination, filters, sorter, extra) => {
                setFilteredInfo(filters);
                onChange?.(pagination, filters, sorter, extra);
            }}
            locale={{
                emptyText: (
                    <EmptyState
                        {...emptyState}
                        subject={subject}
                        filter={{
                            ...filter,
                            hasOtherFilters: filter?.hasOtherFilters || hasColumnFilters,
                            onClear: () => {
                                filter?.onClear();
                                setFilteredInfo({});
                            },
                        }}
                        loading={isLoading}
                        error={hasFailed(query)}
                        onRetry={query.refetch}
                    />
                ),
            }}
        />
    );
}
