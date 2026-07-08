import { Table, type TableColumnsType, type TableProps } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    type OutputPortInputPort,
    type RemoveOutputPortAsInputPortApiArg,
    type RenewOutputPortAsInputPortApiArg,
    useRemoveOutputPortAsInputPortMutation,
    useRenewOutputPortAsInputPortMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions.ts';
import { usePendingActionHandlers } from '@/utils/pending-request.helper.ts';
import styles from './consumers-table.module.scss';
import { getConsumerColumns } from './consumers-table-columns.tsx';

type Props = {
    dataProductId: string;
    outputPortId: string;
    dataProducts: OutputPortInputPort[];
    isLoading?: boolean;
};

export function ConsumersTable({ outputPortId, dataProductId, dataProducts, isLoading }: Props) {
    const { t } = useTranslation();
    const [removeOutputPortAsInputPort, { isLoading: isRemovingOutputPortAsInputPort }] =
        useRemoveOutputPortAsInputPortMutation();

    const [renewOutputPortAsInputPort, { isLoading: isRenewingOutputPortAsInputPort }] =
        useRenewOutputPortAsInputPortMutation();

    const {
        handleAcceptDataProductDatasetLink,
        handleRejectDataProductDatasetLink,

        isApprovingDataProductLink,
        isRejectingDataProductLink,
    } = usePendingActionHandlers();

    const { data: approve_access } = useCheckAccessQuery(
        {
            resource: outputPortId,
            action: AuthorizationAction.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
        },
        { skip: !outputPortId },
    );
    const { data: revoke_access } = useCheckAccessQuery(
        {
            resource: outputPortId,
            action: AuthorizationAction.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS,
        },
        { skip: !outputPortId },
    );
    const canApprove = approve_access?.allowed || false;
    const canRevoke = revoke_access?.allowed || false;

    const { pagination, handlePaginationChange } = useTablePagination(dataProducts, {
        initialPagination: TABLE_SUBSECTION_PAGINATION,
    });

    const onChange: TableProps<OutputPortInputPort>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleRemoveDatasetFromDataProduct = useCallback(
        async (request: RemoveOutputPortAsInputPortApiArg, consuming_data_product_name: string) => {
            try {
                await removeOutputPortAsInputPort(request).unwrap();
                dispatchMessage({
                    content: t('Removed Data Product {{name}} as Input Port', { name: consuming_data_product_name }),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to remove Output Port from Data Product {{name}}', {
                        name: consuming_data_product_name,
                    }),
                    type: 'error',
                });
            }
        },
        [removeOutputPortAsInputPort, t],
    );

    const handleRenewOutputPortAsInputPort = useCallback(
        async (request: RenewOutputPortAsInputPortApiArg, consuming_data_product_name: string) => {
            try {
                await renewOutputPortAsInputPort(request).unwrap();
                dispatchMessage({
                    content: t('Renewed Data Product {{name}} as Input Port', { name: consuming_data_product_name }),
                    type: 'success',
                });
            } catch (_error) {
                dispatchMessage({
                    content: t('Failed to renew Output Port from Data Product {{name}}', {
                        name: consuming_data_product_name,
                    }),
                    type: 'error',
                });
            }
        },
        [renewOutputPortAsInputPort, t],
    );

    const columns: TableColumnsType<OutputPortInputPort> = useMemo(() => {
        return getConsumerColumns({
            t,
            dataProductId,
            outputPortId,
            dataProductLinks: dataProducts,
            onAcceptDataProductDatasetLink: handleAcceptDataProductDatasetLink,
            onRejectDataProductDatasetLink: handleRejectDataProductDatasetLink,
            onRemoveDataProductDatasetLink: handleRemoveDatasetFromDataProduct,
            onRenewDataProductDatasetLink: handleRenewOutputPortAsInputPort,
            isLoading:
                isRemovingOutputPortAsInputPort ||
                isRejectingDataProductLink ||
                isApprovingDataProductLink ||
                isRenewingOutputPortAsInputPort,
            canApprove: canApprove,
            canRevoke: canRevoke,
        });
    }, [
        t,
        dataProductId,
        outputPortId,
        dataProducts,
        handleAcceptDataProductDatasetLink,
        handleRejectDataProductDatasetLink,
        handleRemoveDatasetFromDataProduct,
        handleRenewOutputPortAsInputPort,
        isApprovingDataProductLink,
        isRejectingDataProductLink,
        isRemovingOutputPortAsInputPort,
        isRenewingOutputPortAsInputPort,
        canApprove,
        canRevoke,
    ]);

    return (
        <Table<OutputPortInputPort>
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
