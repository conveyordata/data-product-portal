import styles from './data-output-tab.module.scss';
import { Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { useTranslation } from 'react-i18next';
import { Searchbar } from '@/components/form';
import { SearchForm } from '@/types/shared';
import { DataOutputLink } from '@/types/dataset';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { DataOutputTable } from '@/pages/dataset/components/dataset-tabs/data-output-tab/components/data-output-table/data-output-table.component.tsx';
import { getIsDatasetOwner } from '@/utils/dataset-user.helper.ts';

type Props = {
    datasetId: string;
};

function filterDataOutputs(dataOutputLinks: DataOutputLink[], searchTerm: string) {
    return (
        dataOutputLinks.filter(
            (item) =>
                item?.data_output?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                item?.data_output?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function DataOutputTab({ datasetId }: Props) {
    const { t } = useTranslation();
    const user = useSelector(selectCurrentUser);
    const { data: dataset, isLoading } = useGetDatasetByIdQuery(datasetId);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const datasetDataOutputs = useMemo(() => {
        return dataset?.data_output_links || [];
    }, [dataset?.id, dataset?.data_output_links]);

    const filteredDataOutputs = useMemo(() => {
        return filterDataOutputs(datasetDataOutputs, searchTerm);
    }, [dataset?.data_output_links, searchTerm]);

    const isDatasetOwner = useMemo(() => {
        if (!dataset || !user) return false;

        return getIsDatasetOwner(dataset, user.id) || user.is_admin;
    }, [dataset?.id, user?.id]);

    return (
        <>
            <Flex vertical className={styles.container}>
                <Searchbar
                    placeholder={t('Search data products by name')}
                    formItemProps={{ initialValue: '' }}
                    form={searchForm}
                />

                <DataOutputTable
                    dataOutputs={filteredDataOutputs}
                    isLoading={isLoading}
                    datasetId={datasetId}
                    isCurrentDatasetOwner={isDatasetOwner}
                    currentUserId={user?.id}
                />
            </Flex>
            {/* Todo - Allow to initiate data-product-dataset-link action from the dataset (for restricted datasets) */}
            {/*{isVisible && <AddDataProductPopup onClose={handleClose} isOpen={isVisible} datasetId={datasetId} />}*/}
        </>
    );
}
