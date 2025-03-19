import { Descriptions, Flex, Form, Input, List, Typography } from 'antd';
import dayjs from 'dayjs';
import { useTranslation } from 'react-i18next';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component.tsx';
import {
    useGetDataProductByIdQuery,
    useGetDataProductHistoryQuery,
} from '@/store/features/data-products/data-products-api-slice.ts';

import styles from './history-tab.module.scss';

type Props = {
    dataProductId: string;
};

type SearchForm = {
    search: string;
};

export function HistoryTab({ dataProductId }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct } = useGetDataProductByIdQuery(dataProductId);
    const { data: history } = useGetDataProductHistoryQuery(dataProductId);
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
                    pagination={{
                        pageSize: 5, // Show 5 items per page
                        showSizeChanger: true, // Allow changing the page size
                        pageSizeOptions: ['5', '10', '20'], // Page size options
                    }}
                    renderItem={(item) => {
                        const hasContent = item.user || item.dataset;

                        return (
                            <List.Item className={styles.listItem}>
                                <div className={styles.leftContent}>
                                    <Descriptions
                                        bordered
                                        size="small"
                                        column={2} // Display two items per row
                                        layout="horizontal" // Horizontal layout
                                        title={item.name || t('No title available')}
                                        className={styles.descriptions}
                                    >
                                        {item.user && (
                                            <Descriptions.Item label={t('User')}>{item.user.email}</Descriptions.Item>
                                        )}
                                        {item.dataset && (
                                            <Descriptions.Item label={t('Dataset')}>
                                                {item.dataset.name}
                                            </Descriptions.Item>
                                        )}
                                        {!hasContent && (
                                            <Descriptions.Item>
                                                <Typography.Text type="secondary">
                                                    {t('No additional details available')}
                                                </Typography.Text>
                                            </Descriptions.Item>
                                        )}
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
                        );
                    }}
                />
            ) : (
                <EmptyList
                    description={t(`No data available for data product {{name}}`, { name: dataProduct?.name })}
                />
            )}
        </Flex>
    );
}
