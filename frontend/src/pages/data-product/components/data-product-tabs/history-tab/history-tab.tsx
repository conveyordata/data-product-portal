import { Flex, Form, Input } from 'antd';
import { useTranslation } from 'react-i18next';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component.tsx';
import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';

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
    const [searchForm] = Form.useForm<SearchForm>();

    return (
        <Flex vertical className={styles.container}>
            <Form form={searchForm}>
                <Form.Item<SearchForm> name={'search'}>
                    <Input.Search placeholder={t('Search history by description, type or name')} allowClear />
                </Form.Item>
            </Form>
            <EmptyList description={t(`No data available for data product {{name}}`, { name: dataProduct?.name })} />
        </Flex>
    );
}
