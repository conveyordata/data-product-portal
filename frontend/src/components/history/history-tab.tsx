import { CaretRightOutlined } from '@ant-design/icons';
import { Flex, Form, Input, Table, Typography } from 'antd';
import dayjs from 'dayjs';
import { useTranslation } from 'react-i18next';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component.tsx';
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

import styles from './history-tab.module.scss';

type Props = {
    id: string;
    type: 'dataset' | 'dataproduct' | 'dataoutput';
};

type SearchForm = {
    search: string;
};

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

    const handleSearch = (values: SearchForm) => {
        console.log(values);
    };

    // Define table columns
    const columns = [
        {
            title: t('Event Name'),
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
            title: t('Executed By'),
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
        <div className={styles.container}>
            <Form form={searchForm} onFinish={handleSearch}>
                <Form.Item<SearchForm> name={'search'}>
                    <Input.Search placeholder={t('Search history by description, type or name')} allowClear />
                </Form.Item>
            </Form>
            {history && history.length > 0 ? (
                <Table
                    dataSource={history.map((item, index) => ({ ...item, key: index }))}
                    columns={columns}
                    pagination={{
                        pageSize: 5, // Show 5 items per page
                        showSizeChanger: true, // Allow changing the page size
                        pageSizeOptions: ['5', '10', '20'], // Page size options
                    }}
                />
            ) : (
                <EmptyList description={t(`No history available for {{name}}`, { name: data?.name })} />
            )}
        </div>
    );
}
