import { Flex, Table, type TableColumnsType } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import {
    useGetDataProductByIdQuery,
    useRemoveDatasetFromDataProductMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import type { DatasetLink } from '@/types/data-product';
import { TablePaginationConfig } from '@/types/shared/tables.ts';

import styles from './dataset-table.module.scss';
import { getDataProductDatasetsColumns } from './dataset-table-columns.tsx';

type Props = {
    isCurrentDataProductOwner: boolean;
    dataProductId: string;
    datasets: DatasetLink[];
    pagination: TablePaginationConfig;
};

export function DatasetTable({ isCurrentDataProductOwner, dataProductId, datasets, pagination }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);
    const [removeDatasetFromDataProduct, { isLoading: isRemovingDatasetFromDataProduct }] =
        useRemoveDatasetFromDataProductMutation();

    const handleRemoveDatasetFromDataProduct = useCallback(
        async (datasetId: string, name: string) => {
            try {
                await removeDatasetFromDataProduct({ datasetId, dataProductId: dataProductId }).unwrap();
                dispatchMessage({
                    content: t('Dataset {{name}} has been removed from data product', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to remove dataset from data product', error);
            }
        },
        [dataProductId, removeDatasetFromDataProduct, t],
    );

    const handleCancelDatasetLinkRequest = useCallback(
        async (datasetId: string, name: string) => {
            try {
                await removeDatasetFromDataProduct({ datasetId, dataProductId: dataProductId }).unwrap();
                dispatchMessage({
                    content: t('Request to link dataset {{name}} has been cancelled', { name }),
                    type: 'success',
                });
            } catch (error) {
                console.error('Failed to cancel dataset link request', error);
            }
        },
        [dataProductId, removeDatasetFromDataProduct, t],
    );

    const columns: TableColumnsType<DatasetLink> = useMemo(() => {
        return getDataProductDatasetsColumns({
            onRemoveDataProductDatasetLink: handleRemoveDatasetFromDataProduct,
            onCancelDataProductDatasetLinkRequest: handleCancelDatasetLinkRequest,
            t,
            datasetLinks: datasets,
            isDisabled: !isCurrentDataProductOwner,
            isLoading: isRemovingDatasetFromDataProduct,
        });
    }, [
        handleRemoveDatasetFromDataProduct,
        handleCancelDatasetLinkRequest,
        t,
        datasets,
        isCurrentDataProductOwner,
        isRemovingDatasetFromDataProduct,
    ]);

    if (!dataProduct) return null;

    return (
        <Flex className={styles.datasetListContainer}>
            <Table<DatasetLink>
                loading={isLoadingDataProduct}
                className={styles.datasetListTable}
                columns={columns}
                dataSource={datasets}
                rowKey={({ id }) => id}
                pagination={{
                    ...pagination,
                    style: { display: 'none' },
                }}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
