import { Flex, Form, Input, List } from 'antd';
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
                    dataSource={history}
                    renderItem={(item) => (
                        <List.Item>
                            <List.Item.Meta
                                title={item.name || t('No title available')}
                                description={
                                    <>
                                        {item.data_product && (
                                            <p>
                                                <strong>{t('Data Product')}:</strong> {item.data_product.name}
                                            </p>
                                        )}
                                        {item.user && (
                                            <p>
                                                <strong>{t('User')}:</strong> {item.user.email}
                                            </p>
                                        )}
                                        {item.dataset && (
                                            <p>
                                                <strong>{t('Dataset')}:</strong> {item.dataset.name}
                                            </p>
                                        )}
                                    </>
                                }
                            />
                        </List.Item>
                    )}
                />
            ) : (
                <EmptyList
                    description={t(`No data available for data product {{name}}`, { name: dataProduct?.name })}
                />
            )}
        </Flex>
    );
}
