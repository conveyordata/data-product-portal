import { Table, type TableColumnsType, type TableProps } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { acceptRequest, rejectRequest } from '@/components/pending-access-requests-modal/request-handlers.ts';
import { ReviewRequestModal } from '@/components/pending-access-requests-modal/review-request-modal.tsx';
import { TABLE_SUBSECTION_PAGINATION } from '@/constants/table.constants.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import {
    type OutputPortInputPort,
    useRemoveOutputPortAsInputPortMutation,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { useGetUserPendingActionsQuery } from '@/store/api/services/generated/usersApi.ts';
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

    const [reviewingOutputPortInputPortId, setReviewingOutputPortInputPortId] = useState<string | null>(null);

    const { data: { pending_actions } = {} } = useGetUserPendingActionsQuery();
    const handlers = usePendingActionHandlers();

    const reviewingPendingAction = pending_actions?.find((action) => action.id === reviewingOutputPortInputPortId);

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
        async (dataProductId: string, consumingDataProductName: string, consumingDataProductId: string) => {
            try {
                await removeOutputPortAsInputPort({
                    outputPortId: outputPortId,
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
        [outputPortId, removeOutputPortAsInputPort, t],
    );

    const columns: TableColumnsType<OutputPortInputPort> = useMemo(() => {
        return getConsumerColumns({
            t,
            dataProductId,
            outputPortId,
            dataProductLinks: dataProducts,
            onRemoveDataProductDatasetLink: handleRemoveDatasetFromDataProduct,
            isLoading: isRemovingOutputPortAsInputPort || isRejectingDataProductLink || isApprovingDataProductLink,
            canApprove: canApprove,
            canRevoke: canRevoke,
            setReviewingOutputPortInputPortId,
        });
    }, [
        t,
        dataProductId,
        outputPortId,
        dataProducts,
        handleAcceptDataProductDatasetLink,
        handleRejectDataProductDatasetLink,
        handleRemoveDatasetFromDataProduct,
        isApprovingDataProductLink,
        isRejectingDataProductLink,
        isRemovingOutputPortAsInputPort,
        canApprove,
        canRevoke,
    ]);

    return (
        <>
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
            {
                <ReviewRequestModal
                    action={reviewingPendingAction}
                    open={reviewingPendingAction !== null}
                    onClose={() => setReviewingOutputPortInputPortId(null)}
                    onAccept={(action, reasoning) => acceptRequest(action, handlers, reasoning)}
                    onReject={(action, reasoning) => rejectRequest(action, handlers, reasoning)}
                />
            }
        </>
    );
}
