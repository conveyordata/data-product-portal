import { Flex, Form, Table, type TableProps } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { TFunction } from 'i18next';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { HISTORY_PAGINATION } from '@/constants/table.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import type { EventContract } from '@/types/events/event.contract';
import type { EventReferenceEntity } from '@/types/events/event-reference-entity';
import type { SearchForm } from '@/types/shared';
import { getEventTypeDisplayText, getSubjectDisplayLabel, getTargetDisplayLabel } from '@/utils/history.helper.tsx';
import { Searchbar } from '../form';
import styles from './history-tab.module.scss';
import { getHistoryColumns } from './history-table-columns';

type Event = EventContract & { key: number };

function filterHistory(
    t: TFunction,
    events: EventContract[],
    searchTerm: string,
    resourceId: string,
    type: EventReferenceEntity,
): Event[] {
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

        const text = getEventTypeDisplayText(t, record.name, record.target_type, label);
        return text.toLowerCase().includes(searchTerm.toLowerCase());
    });
}

type Props = {
    id: string;
    type: EventReferenceEntity;
    history?: EventContract[];
    isFetching: boolean;
};
export function HistoryTab({ id, type, history = [], isFetching }: Props) {
    const { t } = useTranslation();
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredHistory = useMemo(() => {
        return filterHistory(t, history, searchTerm, id, type);
    }, [t, history, searchTerm, id, type]);

    const { pagination, handlePaginationChange } = useTablePagination(filteredHistory, {
        initialPagination: HISTORY_PAGINATION,
    });

    const onChange: TableProps<Event>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const columns = useMemo(() => getHistoryColumns({ t, resourceId: id, type }), [t, id, type]) as ColumnsType<Event>;

    return (
        <Flex vertical className={`${styles.container} ${filteredHistory?.length === 0 && styles.paginationGap}`}>
            <Searchbar
                form={searchForm}
                formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                placeholder={t('Search event history')}
            />
            <Table<Event>
                loading={isFetching}
                dataSource={filteredHistory}
                columns={columns}
                onChange={onChange}
                size={'small'}
                pagination={{
                    ...pagination,
                    size: 'small',
                    position: ['topRight'],
                    className: styles.pagination,
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{total}} history items', {
                            range0: range[0],
                            range1: range[1],
                            total: total,
                        }),
                }}
            />
        </Flex>
    );
}
