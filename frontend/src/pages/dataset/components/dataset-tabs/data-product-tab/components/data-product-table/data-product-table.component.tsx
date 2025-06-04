import { Flex, Table, type TableColumnsType, type TableProps } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice.ts';
import { useRemoveDataProductDatasetLinkMutation } from '@/store/features/data-products-datasets/data-products-datasets-api-slice.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { DataProductLink } from '@/types/dataset';
import { usePendingActionHandlers } from '@/utils/pending-request.helper.ts';

import { getDatasetDataProductsColumns } from './data-product-table-columns.tsx';
import styles from './data-product-table.module.scss';

type Props = {
    datasetId: string;
    dataProducts: DataProductLink[];
    isLoading?: boolean;
};

export function DataProductTable({ datasetId, dataProducts, isLoading }: Props) {
    const { t } = useTranslation();
    const [removeDatasetFromDataProduct, { isLoading: isRemovingDatasetFromDataProduct }] =
        useRemoveDataProductDatasetLinkMutation();

    const {
        handleAcceptDataProductDatasetLink,
        handleRejectDataProductDatasetLink,

        isApprovingDataProductLink,
        isRejectingDataProductLink,
    } = usePendingActionHandlers();

    const { data: approve_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
        },
        { skip: !datasetId },
    );
    const { data: revoke_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.DATASET__REVOKE_DATAPRODUCT_ACCESS,
        },
        { skip: !datasetId },
    );
    const canApprove = approve_access?.allowed || false;
    const canRevoke = revoke_access?.allowed || false;

    const { pagination, handlePaginationChange } = useTablePagination(dataProducts, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<DataProductLink>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

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

    const columns: TableColumnsType<DataProductLink> = useMemo(() => {
        return getDatasetDataProductsColumns({
            t,
            dataProductLinks: dataProducts,
            onAcceptDataProductDatasetLink: handleAcceptDataProductDatasetLink,
            onRejectDataProductDatasetLink: handleRejectDataProductDatasetLink,
            onRemoveDataProductDatasetLink: handleRemoveDatasetFromDataProduct,
            isLoading: isRemovingDatasetFromDataProduct || isRejectingDataProductLink || isApprovingDataProductLink,
            canApprove: canApprove,
            canRevoke: canRevoke,
        });
    }, [
        t,
        dataProducts,
        handleAcceptDataProductDatasetLink,
        handleRejectDataProductDatasetLink,
        handleRemoveDatasetFromDataProduct,
        isApprovingDataProductLink,
        isRejectingDataProductLink,
        isRemovingDatasetFromDataProduct,
        canApprove,
        canRevoke,
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
