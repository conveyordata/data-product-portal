import { CaretRightOutlined } from '@ant-design/icons';
import { Flex, Form, Table, TableProps, Typography } from 'antd';
import dayjs from 'dayjs';
import { TFunction } from 'i18next';
import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component.tsx';
import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants';
import { useTablePagination } from '@/hooks/use-table-pagination';
import {
    useGetDataOutputByIdQuery,
    useGetDataOutputHistoryQuery,
} from '@/store/features/data-outputs/data-outputs-api-slice';
import {
    useGetDataProductByIdQuery,
    useGetDataProductHistoryQuery,
} from '@/store/features/data-products/data-products-api-slice';
import { useGetDatasetByIdQuery, useGetDatasetHistoryQuery } from '@/store/features/datasets/datasets-api-slice';
import { EventContract } from '@/types/events/event.contract';
import { getSubjectDisplayLabel, getTargetDisplayLabel } from '@/utils/history.helper';

import { Searchbar } from '../form';
import styles from './history-tab.module.scss';

type Props = {
    id: string;
    type: 'dataset' | 'dataproduct' | 'dataoutput';
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
            event.name?.toLowerCase().includes(searchTerm?.toLowerCase())
        );
    });
}

export function HistoryTab({ id, type }: Props) {
    const dataProductQuery = useGetDataProductByIdQuery(id, { skip: type !== 'dataproduct' || !id });
    const datasetQuery = useGetDatasetByIdQuery(id, { skip: type !== 'dataset' || !id });
    const dataOutputQuery = useGetDataOutputByIdQuery(id, { skip: type !== 'dataoutput' || !id });
    const dataOutputHistoryQuery = useGetDataOutputHistoryQuery(id, { skip: !id });
    const dataProductHistoryQuery = useGetDataProductHistoryQuery(id, { skip: !id });
    const datasetHistoryQuery = useGetDatasetHistoryQuery(id, { skip: !id });

    let dataQuery;
    let historyQuery;

    switch (type) {
        case 'dataproduct':
            dataQuery = dataProductQuery;
            historyQuery = dataProductHistoryQuery;
            break;
        case 'dataset':
            dataQuery = datasetQuery;
            historyQuery = datasetHistoryQuery;
            break;
        case 'dataoutput':
            dataQuery = dataOutputQuery;
            historyQuery = dataOutputHistoryQuery;
            break;
    }

    const { t } = useTranslation();
    const { data: data } = dataQuery;
    const { data: history } = historyQuery;
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

    // Define table columns
    const columns = [
        {
            title: t('Event name'),
            dataIndex: 'name',
            key: 'name',
            render: (text: string) => text || t('No title available'),
        },
        {
            title: t('Involved entities'),
            key: 'Detail',
            render: (record: EventContract) => {
                const subjectLabel = getSubjectDisplayLabel(t, record);
                const targetLabel = getTargetDisplayLabel(t, record);

                if (targetLabel) {
                    return (
                        <Flex vertical>
                            <Typography.Text>{subjectLabel}</Typography.Text>
                            <Typography.Text>
                                <CaretRightOutlined /> {targetLabel}
                            </Typography.Text>
                        </Flex>
                    );
                }
                return <Typography.Text>{subjectLabel}</Typography.Text>;
            },
        },
        {
            title: t('Executed by'),
            dataIndex: 'actor',
            key: 'actor',
            render: (actor: { first_name: string; last_name: string }) => `${actor.first_name} ${actor.last_name}`,
        },
        {
            title: t('Timestamp'),
            dataIndex: 'created_on',
            key: 'created_on',
            render: (created_on: string) => `${dayjs(created_on).format('YYYY-MM-DD HH:mm')} ${t('UTC')}`,
        },
    ];

    return (
        <Flex vertical className={`${styles.container} ${filteredHistory?.length === 0 && styles.paginationGap}`}>
            <Searchbar
                form={searchForm}
                formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                placeholder={t('Search event history')}
            />
            {filteredHistory && filteredHistory.length > 0 ? (
                <Table<EventContract>
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
                />
            ) : (
                <EmptyList description={t(`No history available for {{name}}`, { name: data?.name })} />
            )}
        </Flex>
    );
}
