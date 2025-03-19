import { Descriptions, Flex, Form, Input, List, Typography } from 'antd';
import dayjs from 'dayjs';
import { useTranslation } from 'react-i18next';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component.tsx';
import { useGetDatasetByIdQuery, useGetDatasetHistoryQuery } from '@/store/features/datasets/datasets-api-slice';

import styles from './history-tab.module.scss';

type Props = {
    datasetId: string;
};

type SearchForm = {
    search: string;
};

export function HistoryTab({ datasetId }: Props) {
    const { t } = useTranslation();
    const { data: dataset } = useGetDatasetByIdQuery(datasetId);
    const { data: history } = useGetDatasetHistoryQuery(datasetId);
    const [searchForm] = Form.useForm<SearchForm>();

    const handleSearch = (values: SearchForm) => {
        console.log(values);
    };

    return (
        <Flex vertical className={styles.container}>
            <Form form={searchForm} onFinish={handleSearch}>
                <Form.Item<SearchForm> name={'search'}>
                    <Input.Search placeholder={t('Search history by description, type or name')} allowClear />
                </Form.Item>
            </Form>
            {history && history.length > 0 ? (
                <List
                    dataSource={[...history].sort((a, b) => dayjs(b.created_on).diff(dayjs(a.created_on)))}
                    renderItem={(item) => (
                        <List.Item className={styles.listItem}>
                            <div className={styles.leftContent}>
                                <Descriptions
                                    bordered
                                    size="small"
                                    column={1}
                                    title={item.name || t('No title available')}
                                >
                                    {item.data_product && (
                                        <Descriptions.Item label={t('Data Product')}>
                                            {item.data_product.name}
                                        </Descriptions.Item>
                                    )}
                                    {item.user && (
                                        <Descriptions.Item label={t('User')}>{item.user.email}</Descriptions.Item>
                                    )}
                                    {/* {item.dataset && (
                                        <Descriptions.Item label={t('Dataset')}>
                                            {item.dataset.name}
                                        </Descriptions.Item>
                                    )} */}
                                </Descriptions>
                            </div>
                            <div className={styles.rightContent}>
                                <Typography.Text type="secondary" className={styles.actor}>
                                    {item.actor.first_name} {item.actor.last_name}
                                </Typography.Text>
                                <Typography.Text type="secondary" className={styles.timestamp}>
                                    {dayjs(item.created_on).format('YYYY-MM-DD HH:mm')} {t('UTC')}
                                </Typography.Text>
                            </div>
                        </List.Item>
                    )}
                />
            ) : (
                <EmptyList description={t(`No data available for dataset {{name}}`, { name: dataset?.name })} />
            )}
        </Flex>
    );
}
