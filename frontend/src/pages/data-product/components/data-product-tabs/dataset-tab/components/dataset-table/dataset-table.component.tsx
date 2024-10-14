import { Flex, Table, TableColumnsType } from 'antd';
import { useMemo } from 'react';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useTranslation } from 'react-i18next';
import {
    useGetDataProductByIdQuery,
    useRemoveDatasetFromDataProductMutation,
} from '@/store/features/data-products/data-products-api-slice.ts';
import styles from './dataset-table.module.scss';
import { getDataProductDatasetsColumns } from './dataset-table-columns.tsx';
import { DatasetLink } from '@/types/data-product';

type Props = {
    isCurrentDataProductOwner: boolean;
    dataProductId: string;
    datasets: DatasetLink[];
};

export function DatasetTable({ isCurrentDataProductOwner, dataProductId, datasets }: Props) {
    const { t } = useTranslation();
    const { data: dataProduct, isLoading: isLoadingDataProduct } = useGetDataProductByIdQuery(dataProductId);
    const [removeDatasetFromDataProduct, { isLoading: isRemovingDatasetFromDataProduct }] =
        useRemoveDatasetFromDataProductMutation();

    const handleRemoveDatasetFromDataProduct = async (datasetId: string, name: string) => {
        try {
            await removeDatasetFromDataProduct({ datasetId, dataProductId: dataProductId }).unwrap();
            dispatchMessage({
                content: t('Dataset {{name}} has been removed from data product', { name }),
                type: 'success',
            });
        } catch (error) {
            console.error('Failed to remove dataset from data product', error);
        }
    };

    const handleCancelDatasetLinkRequest = async (datasetId: string, name: string) => {
        try {
            await removeDatasetFromDataProduct({ datasetId, dataProductId: dataProductId }).unwrap();
            dispatchMessage({
                content: t('Request to link dataset {{name}} has been cancelled', { name }),
                type: 'success',
            });
        } catch (error) {
            console.error('Failed to cancel dataset link request', error);
        }
    };

    const columns: TableColumnsType<DatasetLink> = useMemo(() => {
        return getDataProductDatasetsColumns({
            onRemoveDataProductDatasetLink: handleRemoveDatasetFromDataProduct,
            onCancelDataProductDatasetLinkRequest: handleCancelDatasetLinkRequest,
            t,
            datasetLinks: datasets,
            isDisabled: !isCurrentDataProductOwner,
            isLoading: isRemovingDatasetFromDataProduct,
        });
    }, [dataProductId, t, datasets, isCurrentDataProductOwner]);

    if (!dataProduct) return null;

    return (
        <Flex className={styles.datasetListContainer}>
            <Table<DatasetLink>
                loading={isLoadingDataProduct}
                className={styles.datasetListTable}
                columns={columns}
                dataSource={datasets}
                rowKey={({ id }) => id}
                pagination={false}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
