import { Flex, Form, Input } from 'antd';
import { useTranslation } from 'react-i18next';

import { EmptyList } from '@/components/empty/empty-list/empty-list.component.tsx';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';

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
    const [searchForm] = Form.useForm<SearchForm>();

    return (
        <Flex vertical className={styles.container}>
            <Form form={searchForm}>
                <Form.Item<SearchForm> name={'search'}>
                    <Input.Search placeholder={t('Search history by description, type or name')} allowClear />
                </Form.Item>
            </Form>
            <EmptyList description={t(`No data available for dataset {{name}}`, { name: dataset?.name })} />
        </Flex>
    );
}
