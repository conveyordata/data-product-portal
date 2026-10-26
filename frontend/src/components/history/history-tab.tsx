import { HistoryOutlined } from '@ant-design/icons';
import { Flex, Input, type TableProps } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { TFunction } from 'i18next';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { EmptyStateQuery } from '@/components/empty-state/empty-state.component.tsx';
import { searchFilter } from '@/components/empty-state/empty-state.component.tsx';
import { ListTable } from '@/components/list-table/list-table.component.tsx';
import { HISTORY_PAGINATION } from '@/constants/table.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import type { GetEventHistoryResponseItem } from '@/store/api/services/generated/dataProductsApi.ts';
import type { EventReferenceEntity } from '@/types/events/event-reference-entity';
import { parseEventType } from '@/types/events/event-types.ts';
import { getEventTypeDisplayText, getSubjectDisplayLabel, getTargetDisplayLabel } from '@/utils/history.helper.tsx';
import { getHistoryColumns } from './history-table-columns';

function filterHistory(
    t: TFunction,
    events: GetEventHistoryResponseItem[],
    searchTerm: string,
    resourceId: string,
    type: EventReferenceEntity,
): GetEventHistoryResponseItem[] {
    const items = events.map((item, index) => ({ ...item, key: index }));
    if (!searchTerm) {
        return items;
    }

    return items.filter((record) => {
        const { target_id, subject_id, subject_type, target_type } = record;

        let label = '';
        if (!(subject_id === resourceId && type === subject_type)) {
            label = getSubjectDisplayLabel(record);
        } else if (target_id && !(target_id === resourceId && type === target_type)) {
            label = getTargetDisplayLabel(record);
        }

        const text = getEventTypeDisplayText(t, parseEventType(record.name), label, record.target_type);
        return text.toLowerCase().includes(searchTerm.toLowerCase());
    });
}

type Props = {
    id: string;
    type: EventReferenceEntity;
    history?: GetEventHistoryResponseItem[];
    query: EmptyStateQuery;
};
export function HistoryTab({ id, type, history = [], query }: Props) {
    const { t } = useTranslation();
    const [searchTerm, setSearchTerm] = useState<string>('');

    const filteredHistory = useMemo(() => {
        return filterHistory(t, history, searchTerm, id, type);
    }, [t, history, searchTerm, id, type]);

    const { pagination, handlePaginationChange } = useTablePagination(filteredHistory, {
        initialPagination: HISTORY_PAGINATION,
    });

    const onChange: TableProps<GetEventHistoryResponseItem>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const columns = useMemo(
        () => getHistoryColumns({ t, resourceId: id, type }),
        [t, id, type],
    ) as ColumnsType<GetEventHistoryResponseItem>;

    return (
        <Flex vertical gap="middle">
            <Input.Search
                placeholder={t('Search event history')}
                allowClear
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
            />
            <ListTable<GetEventHistoryResponseItem>
                query={query}
                dataSource={filteredHistory}
                columns={columns}
                subject={t('events')}
                emptyState={{
                    icon: <HistoryOutlined />,
                    title: t('No history yet'),
                    description: t('This tab lists every change made here.'),
                }}
                onChange={onChange}
                filter={searchFilter(searchTerm, setSearchTerm)}
                size="small"
                pagination={{
                    ...pagination,
                    size: 'small',
                    placement: ['topEnd'],
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{count}} history items', {
                            range0: range[0],
                            range1: range[1],
                            count: total,
                        }),
                }}
            />
        </Flex>
    );
}
