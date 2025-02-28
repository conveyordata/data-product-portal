import { Button, Form, List, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import {
    useGetAllDataProductsQuery,
    useRequestDatasetAccessForDataProductMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { DataProductLink } from '@/types/dataset';
import { useCallback, useMemo } from 'react';
import { SearchForm } from '@/types/shared';
import { useGetDatasetByIdQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { DataProductsGetContract } from '@/types/data-product';
import { DataProductDatasetLinkPopup } from '@/components/data-products/data-product-dataset-link-popup/data-product-dataset-link-popup.component.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import styles from '@/pages/data-product/components/data-product-tabs/dataset-tab/components/add-dataset-popup/add-dataset-popup.module.scss';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { DataProductIcon } from '@/types/data-product-type';

type Props = {
    onClose: () => void;
    isOpen: boolean;
    datasetId: string;
};

const filterOutAlreadyLinkedDataProducts = (
    dataProducts: DataProductsGetContract,
    dataProductLinks: DataProductLink[],
) => {
    return (
        dataProducts.filter(
            (dataProduct) =>
                !dataProductLinks?.some((linkedDataProduct) => linkedDataProduct.data_product_id === dataProduct.id),
        ) ?? []
    );
};

const handleDataProductListFilter = (dataProducts: DataProductsGetContract, searchTerm: string) => {
    return dataProducts.filter((dataProduct) => {
        return dataProduct?.name?.toLowerCase().includes(searchTerm.toLowerCase());
    });
};

export function AddDataProductPopup({ onClose, isOpen, datasetId }: Props) {
    const { t } = useTranslation();
    const { data: dataset } = useGetDatasetByIdQuery(datasetId);
    const { data: allDataProducts = [], isFetching: isFetchingDataProducts } = useGetAllDataProductsQuery();
    const [requestDatasetAccessForDataProduct, { isLoading: isRequestingAccess }] =
        useRequestDatasetAccessForDataProductMutation();
    const [searchForm] = Form.useForm<SearchForm>();
    const searchTerm = Form.useWatch('search', searchForm);

    const filteredUnlinkedDataProducts = useMemo(() => {
        const dataProductLinks = dataset?.data_product_links ?? [];

        const unlinkedDataProducts = filterOutAlreadyLinkedDataProducts(allDataProducts, dataProductLinks);
        return searchTerm ? handleDataProductListFilter(unlinkedDataProducts, searchTerm) : unlinkedDataProducts;
    }, [dataset?.data_product_links, allDataProducts, searchTerm]);

    const handleRequestAccessForDataProduct = useCallback(
        async (dataProductId: string) => {
            try {
                await requestDatasetAccessForDataProduct({ datasetId, dataProductId }).unwrap();
                dispatchMessage({ content: t('Dataset access has been requested'), type: 'success' });
            } catch (_error) {
                dispatchMessage({ content: t('Failed to grant access to the data product'), type: 'error' });
            }
        },
        [datasetId, t, requestDatasetAccessForDataProduct],
    );
    return (
        <DataProductDatasetLinkPopup
            isOpen={isOpen}
            onClose={onClose}
            searchForm={searchForm}
            title={t('Add Data Product')}
            searchPlaceholder={t('Search data products by name')}
        >
            <List
                loading={isFetchingDataProducts || isRequestingAccess}
                size={'large'}
                locale={{ emptyText: t('No data products found') }}
                rowKey={({ id }) => id}
                dataSource={filteredUnlinkedDataProducts}
                renderItem={({ id, type, name, status }) => {
                    const icon = (
                        <CustomSvgIconLoader iconComponent={getDataProductTypeIcon(type?.icon_key)} hasRoundBorder />
                    );
                    return (
                        <List.Item key={id}>
                            <TableCellAvatar
                                icon={icon}
                                title={name}
                                subtitle={
                                    <Typography.Link className={styles.noCursorPointer}>{status}</Typography.Link>
                                }
                            />
                            <Button
                                disabled={isRequestingAccess}
                                loading={isRequestingAccess}
                                type={'link'}
                                onClick={() => handleRequestAccessForDataProduct(id)}
                            >
                                {t('Add Data Product')}
                            </Button>
                        </List.Item>
                    );
                }}
            />
        </DataProductDatasetLinkPopup>
    );
}
