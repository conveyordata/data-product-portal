import { Table, type TableColumnsType, type TableProps } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    type InputPort,
    useRemoveOutputPortAsInputPortMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { usePendingActionHandlers } from '@/utils/pending-request.helper.ts';
import styles from './data-product-table.module.scss';
import { getDatasetDataProductsColumns } from './data-product-table-columns.tsx';

type Props = {
    datasetId: string;
    dataProducts: InputPort[];
    isLoading?: boolean;
};

export function DataProductTable({ datasetId, dataProducts, isLoading }: Props) {
    const { t } = useTranslation();
    const [removeDatasetFromDataProduct, { isLoading: isRemovingDatasetFromDataProduct }] =
        useRemoveOutputPortAsInputPortMutation();

    const {
        handleAcceptDataProductDatasetLink,
        handleRejectDataProductDatasetLink,

        isApprovingDataProductLink,
        isRejectingDataProductLink,
    } = usePendingActionHandlers();

    const { data: approve_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
        },
        { skip: !datasetId },
    );
    const { data: revoke_access } = useCheckAccessQuery(
        {
            resource: datasetId,
            action: AuthorizationAction.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS,
        },
        { skip: !datasetId },
    );
    const canApprove = approve_access?.allowed || false;
    const canRevoke = revoke_access?.allowed || false;

    const { pagination, handlePaginationChange } = useTablePagination(dataProducts, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<InputPort>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleRemoveDatasetFromDataProduct = useCallback(
        async (dataProductId: string, consumingDataProductName: string, consumingDataProductId: string) => {
            try {
                await removeDatasetFromDataProduct({
                    outputPortId: datasetId,
                    dataProductId,
                    removeOutputPortAsInputPortRequest: {
                        consuming_data_product_id: consumingDataProductId,
                    },
                }).unwrap();
                dispatchMessage({
                    content: t('Removed Data Product {{name}} as Input Port', { name: consumingDataProductName }),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to remove Output Port from Data Product'),
                    type: 'error',
                });
            }
        },
        [datasetId, removeDatasetFromDataProduct, t],
    );

    const columns: TableColumnsType<InputPort> = useMemo(() => {
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
        <Table<InputPort>
            loading={isLoading}
            columns={columns}
            dataSource={dataProducts}
            rowKey={({ id }) => id}
            onChange={onChange}
            pagination={{
                ...pagination,
                placement: ['topEnd'],
                size: 'small',
                showTotal: (total, range) =>
                    t('Showing {{range0}}-{{range1}} of {{count}} Data Products', {
                        range0: range[0],
                        range1: range[1],
                        count: total,
                    }),
                className: styles.pagination,
            }}
            size={'small'}
        />
    );
}
