import { Flex, Form, Table, TableProps } from 'antd';
import { TFunction } from 'i18next';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { useGetDataOutputHistoryQuery } from '@/store/features/data-outputs/data-outputs-api-slice';
import { useGetDataProductHistoryQuery } from '@/store/features/data-products/data-products-api-slice';
import { useGetDatasetHistoryQuery } from '@/store/features/datasets/datasets-api-slice';
import { EventContract } from '@/types/events/event.contract';
import { EventObject } from '@/types/events/event-object-type';
import { getSubjectDisplayLabel, getTargetDisplayLabel } from '@/utils/history.helper';

import { Searchbar } from '../form';
import styles from './history-tab.module.scss';
import { getHistoryColumns } from './history-table-columns';

type Props = {
    id: string;
    type: EventObject;
};

type SearchForm = {
    search: string;
};

function filterHistory(events: EventContract[], searchTerm: string, t: TFunction) {
    if (!searchTerm) return events;
    if (!events) return [];

    return events.filter((event) => {
        const subjectLabel = getSubjectDisplayLabel(t, event);
        const targetLabel = getTargetDisplayLabel(t, event);

        return (
            subjectLabel?.toLowerCase().includes(searchTerm?.toLowerCase()) ||
            targetLabel?.toLowerCase().includes(searchTerm?.toLowerCase()) ||
            event.name?.toLowerCase().includes(searchTerm?.toLowerCase()) ||
            event.actor.email.toLowerCase().includes(searchTerm?.toLowerCase())
        );
    });
}

export function HistoryTab({ id, type }: Props) {
    const { data: dataOutputHistoryData, isLoading: isFetchingDataOutputHistory } = useGetDataOutputHistoryQuery(id, {
        skip: !id || type != EventObject.DataOutput,
    });
    const { data: dataProductHistoryData, isLoading: isFetchingDataProductHistory } = useGetDataProductHistoryQuery(
        id,
        { skip: !id || type != EventObject.DataProduct },
    );
    const { data: datasetHistoryData, isLoading: isFetchingDatasetHistory } = useGetDatasetHistoryQuery(id, {
        skip: !id || type != EventObject.Dataset,
    });

    let history: EventContract[] | undefined;
    let isFetching;

    switch (type) {
        case EventObject.DataProduct:
            history = dataProductHistoryData;
            isFetching = isFetchingDataProductHistory;
            break;
        case EventObject.Dataset:
            history = datasetHistoryData;
            isFetching = isFetchingDatasetHistory;
            break;
        case EventObject.DataOutput:
            history = dataOutputHistoryData;
            isFetching = isFetchingDataOutputHistory;
            break;
    }

    const { t } = useTranslation();
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredHistory = useMemo(() => {
        return filterHistory(history ?? [], searchTerm, t);
    }, [history, searchTerm, t]);

    const { pagination, handlePaginationChange, resetPagination } = useTablePagination({
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<EventContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    useEffect(() => {
        resetPagination();
    }, [filteredHistory, resetPagination]);

    const columns = useMemo(() => getHistoryColumns({ t, resourceId: id, type }), [t, id, type]);

    return (
        <Flex vertical className={`${styles.container} ${filteredHistory?.length === 0 && styles.paginationGap}`}>
            <Searchbar
                form={searchForm}
                formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                placeholder={t('Search event history')}
            />
            <Table<EventContract>
                loading={isFetching}
                dataSource={filteredHistory.map((item, index) => ({ ...item, key: index }))}
                columns={columns}
                onChange={onChange}
                pagination={{
                    ...pagination,
                    position: ['topRight'],
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{total}} history items', {
                            range0: range[0],
                            range1: range[1],
                            total: total,
                        }),
                    className: styles.pagination,
                }}
                size={'small'}
            />
        </Flex>
    );
}
