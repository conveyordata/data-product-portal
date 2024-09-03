import styles from './history-tab.module.scss';
import { Flex, Form, Input } from 'antd';
import { useTranslation } from 'react-i18next';
import { useGetDataOutputByIdQuery } from '@/store/features/data-outputs/data-outputs-api-slice.ts';
import { EmptyList } from '@/components/empty/empty-list/empty-list.component.tsx';

type Props = {
    dataOutputId: string;
};

type SearchForm = {
    search: string;
};

export function HistoryTab({ dataOutputId }: Props) {
    const { t } = useTranslation();
    const { data: dataOutput } = useGetDataOutputByIdQuery(dataOutputId);
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
            <EmptyList description={t(`No data available for data output {{name}}`, { name: dataOutput?.name })} />
        </Flex>
    );
}
