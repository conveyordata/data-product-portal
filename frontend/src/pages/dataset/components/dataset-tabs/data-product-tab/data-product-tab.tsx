import styles from './data-product-tab.module.scss';
import { Flex, Form } from 'antd';
import { useMemo } from 'react';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { useTranslation } from 'react-i18next';
import { Searchbar } from '@/components/form';
import { SearchForm } from '@/types/shared';
import { DataProductLink } from '@/types/dataset';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { DataProductTable } from '@/pages/dataset/components/dataset-tabs/data-product-tab/components/data-product-table/data-product-table.component.tsx';
import { getIsDatasetOwner } from '@/utils/dataset-user.helper.ts';

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
    const user = useSelector(selectCurrentUser);
    const { data: dataset, isLoading } = useGetDatasetByIdQuery(datasetId);
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const datasetDataProducts = useMemo(() => {
        return dataset?.data_product_links || [];
    }, [dataset?.id, dataset?.data_product_links]);

    const filteredDataProducts = useMemo(() => {
        return filterDataProducts(datasetDataProducts, searchTerm);
    }, [dataset?.data_product_links, searchTerm]);

    const isDatasetOwner = useMemo(() => {
        if (!dataset || !user) return false;

        return getIsDatasetOwner(dataset, user.id);
    }, [dataset?.id, user?.id]);

    return (
        <>
            <Flex vertical className={styles.container}>
                <Searchbar
                    placeholder={t('Search data products by name')}
                    formItemProps={{ initialValue: '' }}
                    form={searchForm}
                />

                <DataProductTable
                    dataProducts={filteredDataProducts}
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
