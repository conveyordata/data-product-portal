import { Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Searchbar } from '@/components/form';
import { DataOutputTable } from '@/pages/dataset/components/dataset-tabs/data-output-tab/components/data-output-table/data-output-table.component';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
import type { DataOutputLink } from '@/types/dataset';
import type { SearchForm } from '@/types/shared';

import styles from './data-output-tab.module.scss';

function filterDataOutputs(dataOutputLinks: DataOutputLink[], searchTerm: string) {
    return (
        dataOutputLinks.filter(
            (item) =>
                item?.data_output?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                item?.data_output?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

type Props = {
    datasetId: string;
};
export function DataOutputTab({ datasetId }: Props) {
    const { t } = useTranslation();
    const { data: dataset, isLoading } = useGetDatasetByIdQuery(datasetId);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const datasetDataOutputs = useMemo(() => {
        return dataset?.data_output_links || [];
    }, [dataset?.data_output_links]);

    const filteredDataOutputs = useMemo(() => {
        return filterDataOutputs(datasetDataOutputs, searchTerm);
    }, [datasetDataOutputs, searchTerm]);

    return (
        <>
            <Flex
                vertical
                className={`${styles.container} ${filteredDataOutputs.length === 0 && styles.paginationGap}`}
            >
                <Searchbar
                    placeholder={t('Search data outputs by name')}
                    formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                    form={searchForm}
                />

                <DataOutputTable dataOutputs={filteredDataOutputs} isLoading={isLoading} datasetId={datasetId} />
            </Flex>
            {/* Todo - Allow to initiate data-product-dataset-link action from the dataset (for restricted datasets) */}
            {/*{isVisible && <AddDataProductPopup onClose={handleClose} isOpen={isVisible} datasetId={datasetId} />}*/}
        </>
    );
}
