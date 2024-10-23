import { Flex, Table, TableColumnsType } from 'antd';
import { useMemo } from 'react';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { useTranslation } from 'react-i18next';
import styles from './data-product-table.module.scss';
import { getDatasetDataProductsColumns } from './data-product-table-columns.tsx';
import { DataProductLink } from '@/types/dataset';
import {
    useApproveDataProductLinkMutation,
    useRejectDataProductLinkMutation,
    useRemoveDataProductDatasetLinkMutation,
} from '@/store/features/data-products-datasets/data-products-datasets-api-slice.ts';
import { DataProductDatasetLinkRequest } from '@/types/data-product-dataset';

type Props = {
    isCurrentDatasetOwner: boolean;
    datasetId: string;
    dataProducts: DataProductLink[];
    currentUserId?: string;
    isLoading?: boolean;
};

export function DataProductTable({ isCurrentDatasetOwner, datasetId, dataProducts, isLoading }: Props) {
    const { t } = useTranslation();
    const [approveDataProductLink, { isLoading: isApprovingLink }] = useApproveDataProductLinkMutation();
    const [rejectDataProductLink, { isLoading: isRejectingLink }] = useRejectDataProductLinkMutation();
    const [removeDatasetFromDataProduct, { isLoading: isRemovingDatasetFromDataProduct }] =
        useRemoveDataProductDatasetLinkMutation();

    const handleRemoveDatasetFromDataProduct = async (dataProductId: string, name: string, datasetLinkId: string) => {
        try {
            await removeDatasetFromDataProduct({ datasetId, dataProductId, datasetLinkId }).unwrap();
            dispatchMessage({
                content: t('Dataset {{name}} has been removed from data product', { name }),
                type: 'success',
            });
        } catch (_error) {
            dispatchMessage({
                content: t('Failed to remove dataset from data product'),
                type: 'error',
            });
        }
    };

    const handleAcceptDataProductDatasetLink = async (request: DataProductDatasetLinkRequest) => {
        try {
            await approveDataProductLink(request).unwrap();
            dispatchMessage({
                content: t('Dataset request has been successfully approved'),
                type: 'success',
            });
        } catch (_error) {
            dispatchMessage({
                content: t('Failed to approve data product dataset link'),
                type: 'error',
            });
        }
    };

    const handleRejectDataProductDatasetLink = async (request: DataProductDatasetLinkRequest) => {
        try {
            await rejectDataProductLink(request).unwrap();
            dispatchMessage({
                content: t('Dataset access request has been successfully rejected'),
                type: 'success',
            });
        } catch (_error) {
            dispatchMessage({
                content: t('Failed to reject data product dataset link'),
                type: 'error',
            });
        }
    };

    const columns: TableColumnsType<DataProductLink> = useMemo(() => {
        return getDatasetDataProductsColumns({
            onRemoveDataProductDatasetLink: handleRemoveDatasetFromDataProduct,
            t,
            dataProductLinks: dataProducts,
            isDisabled: !isCurrentDatasetOwner,
            isLoading: isRemovingDatasetFromDataProduct || isRejectingLink || isApprovingLink,
            isCurrentDatasetOwner,
            onRejectDataProductDatasetLink: handleRejectDataProductDatasetLink,
            onAcceptDataProductDatasetLink: handleAcceptDataProductDatasetLink,
        });
    }, [datasetId, t, dataProducts, isCurrentDatasetOwner]);

    return (
        <Flex className={styles.datasetListContainer}>
            <Table<DataProductLink>
                loading={isLoading}
                className={styles.datasetListTable}
                columns={columns}
                dataSource={dataProducts}
                rowKey={({ id }) => id}
                pagination={false}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
