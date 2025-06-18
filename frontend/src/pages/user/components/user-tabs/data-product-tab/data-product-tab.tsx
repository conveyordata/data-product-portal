import { Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Searchbar } from '@/components/form';
import { DataProductTable } from '@/pages/dataset/components/dataset-tabs/data-product-tab/components/data-product-table/data-product-table.component';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice';
import type { DataProductLink } from '@/types/dataset';
import type { SearchForm } from '@/types/shared';

import styles from './data-product-tab.module.scss';

type Props = {
    datasetId: string;
};

function filterDataProducts(dataProductLinks: DataProductLink[], searchTerm: string) {
    return (
        dataProductLinks.filter(
            (item) =>
                item?.data_product?.name?.toLowerCase()?.includes(searchTerm?.toLowerCase()) ||
                item?.data_product?.description?.toLowerCase()?.includes(searchTerm?.toLowerCase()),
        ) ?? []
    );
}

export function DataProductTab({ datasetId }: Props) {
    const { t } = useTranslation();
    const { data: dataset, isLoading } = useGetDatasetByIdQuery(datasetId);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const datasetDataProducts = useMemo(() => {
        return dataset?.data_product_links || [];
    }, [dataset?.data_product_links]);

    const filteredDataProducts = useMemo(() => {
        return filterDataProducts(datasetDataProducts, searchTerm);
    }, [datasetDataProducts, searchTerm]);

    return (
        <>
            <Flex
                vertical
                className={`${styles.container} ${filteredDataProducts.length === 0 && styles.paginationGap}`}
            >
                <Searchbar
                    placeholder={t('Search data products by name')}
                    formItemProps={{ initialValue: '', className: styles.marginBottomLarge }}
                    form={searchForm}
                />

                <DataProductTable datasetId={datasetId} dataProducts={filteredDataProducts} isLoading={isLoading} />
            </Flex>
            {/* Todo - Allow to initiate data-product-dataset-link action from the dataset (for restricted datasets) */}
            {/*{isVisible && <AddDataProductPopup onClose={handleClose} isOpen={isVisible} datasetId={datasetId} />}*/}
        </>
    );
}
