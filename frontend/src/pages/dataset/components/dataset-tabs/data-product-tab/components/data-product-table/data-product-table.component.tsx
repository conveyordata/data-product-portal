import { Flex, Table, TableColumnsType, TableProps } from 'antd';
import { useCallback, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import {
    useApproveDataProductLinkMutation,
    useRejectDataProductLinkMutation,
    useRemoveDataProductDatasetLinkMutation,
} from '@/store/features/data-products-datasets/data-products-datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { DataProductDatasetLinkRequest } from '@/types/data-product-dataset';
import { DataProductLink } from '@/types/dataset';

import styles from './data-product-table.module.scss';
import { getDatasetDataProductsColumns } from './data-product-table-columns.tsx';

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

    const { data: access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
        },
        { skip: !datasetId },
    );
    const canApproveNew = access?.allowed || false;
    const { data: revoke_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__REVOKE_DATAPRODUCT_ACCESS,
        },
        { skip: !datasetId },
    );
    const canRevokeNew = revoke_access?.allowed || false;

    const { pagination, handlePaginationChange, resetPagination } = useTablePagination({
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<DataProductLink>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    useEffect(() => {
        resetPagination();
    }, [dataProducts, resetPagination]);

    const handleRemoveDatasetFromDataProduct = useCallback(
        async (dataProductId: string, name: string, datasetLinkId: string) => {
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
        },
        [datasetId, removeDatasetFromDataProduct, t],
    );

    const handleAcceptDataProductDatasetLink = useCallback(
        async (request: DataProductDatasetLinkRequest) => {
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
        },
        [approveDataProductLink, t],
    );

    const handleRejectDataProductDatasetLink = useCallback(
        async (request: DataProductDatasetLinkRequest) => {
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
        },
        [rejectDataProductLink, t],
    );

    const columns: TableColumnsType<DataProductLink> = useMemo(() => {
        return getDatasetDataProductsColumns({
            onRemoveDataProductDatasetLink: handleRemoveDatasetFromDataProduct,
            t,
            dataProductLinks: dataProducts,
            isDisabled: !isCurrentDatasetOwner,
            isLoading: isRemovingDatasetFromDataProduct || isRejectingLink || isApprovingLink,
            isCurrentDatasetOwner,
            canApproveNew,
            canRevokeNew,
            onRejectDataProductDatasetLink: handleRejectDataProductDatasetLink,
            onAcceptDataProductDatasetLink: handleAcceptDataProductDatasetLink,
        });
    }, [
        handleRemoveDatasetFromDataProduct,
        t,
        dataProducts,
        isCurrentDatasetOwner,
        isRemovingDatasetFromDataProduct,
        isRejectingLink,
        isApprovingLink,
        canApproveNew,
        canRevokeNew,
        handleRejectDataProductDatasetLink,
        handleAcceptDataProductDatasetLink,
    ]);

    return (
        <Flex className={styles.datasetListContainer}>
            <Table<DataProductLink>
                loading={isLoading}
                className={styles.datasetListTable}
                columns={columns}
                dataSource={dataProducts}
                rowKey={({ id }) => id}
                onChange={onChange}
                pagination={{
                    ...pagination,
                    position: ['topRight'],
                    size: 'small',
                    showTotal: (total, range) =>
                        t('Showing {{range0}}-{{range1}} of {{total}} data products', {
                            range0: range[0],
                            range1: range[1],
                            total: total,
                        }),
                    className: styles.pagination,
                }}
                rowClassName={styles.tableRow}
                size={'small'}
            />
        </Flex>
    );
}
